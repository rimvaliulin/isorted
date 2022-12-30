"""isorted plugin."""
import itertools
import os
import re
import subprocess

import sublime
import sublime_plugin

encoding_re = re.compile(r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")
option_name_re = re.compile(r"^(:?[a-z]{1,2}|[a-z][a-z_-]+[a-z])$")


class IsortFileCommand(sublime_plugin.TextCommand):
    """isort_file command class."""

    plugin_options = ("isort_command", "isort_on_save")

    def is_enabled(self):
        """Check file is python."""
        return self.view.match_selector(0, "source.python")

    is_visible = is_enabled

    def run(self, edit):
        """Run plugin."""
        positions = list(self.view.sel())
        content = self.view.substr(sublime.Region(0, self.view.size()))
        encoding = self.encoding

        try:
            proc = subprocess.Popen(
                self.command_line,
                cwd=self.working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=self.startup_info,
            )
            out, err = proc.communicate(input=content.encode(encoding), timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        except (UnboundLocalError, OSError) as e:
            msg = "isorted: You may need to install isort and/or configure 'isort_command' in isorted's settings."
            sublime.error_message("%s: %s\n\n%s" % (e.__class__.__name__, e, msg))
            raise Exception(msg)

        if proc.returncode or err:
            sublime.error_message("isort: %s" % err.decode(encoding).split("isort: error: ")[-1:][0])
            return

        self.view.replace(edit, sublime.Region(0, self.view.size()), out.decode(encoding))
        # Our selection has moved now...
        remove_selection = self.view.sel()[0]
        self.view.sel().subtract(remove_selection)
        for position in positions:
            self.view.sel().add(position)

    @property
    def command_line(self):
        """Get command line."""
        settings = self.settings
        try:
            cmd = settings["isort_command"]
            assert cmd and (isinstance(cmd, str) or isinstance(cmd, list) and all(isinstance(c, str) for c in cmd))
        except (KeyError, AssertionError) as e:
            msg = "isorted: 'isort_command' not properly configured. Problem with settings?"
            sublime.error_message(msg)
            raise Exception(msg) from e
        if isinstance(cmd, str):
            cmd = [cmd]
        window_context = self.view.window().extract_variables()
        cmd = [sublime.expand_variables(os.path.expanduser(c), window_context) for c in cmd]
        cmd.extend(self.get_options(settings))
        cmd.append("-")  # set isort in input/ouput mode with -
        return cmd

    @property
    def working_dir(self):
        """Get working directory."""
        filename = self.view.file_name()
        if filename:
            return os.path.dirname(filename)
        window = self.view.window()
        if not window:
            return None
        folders = window.folders()
        if not folders:
            return None
        return folders[0]

    @property
    def startup_info(self):
        """Prepare popen for Windows."""
        startup_info = None
        # win32: hide console window
        if sublime.platform() == "windows":
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = subprocess.SW_HIDE
        return startup_info

    @property
    def settings(self):
        """Get settings."""
        settings = {}
        # Get plugin settings
        plugin_settings = sublime.load_settings("isorted.sublime-settings")
        for name in self.plugin_options:
            settings[name] = plugin_settings.get(name)
        settings.update(plugin_settings.get("options"))
        # Get project settings
        for name, value in self.view.window().project_data()["settings"].items():
            if name.startswith("isorted.") and len(name) > 8:
                settings[name[8:]] = value
            elif name == "isorted":
                for k, v in value.items():
                    settings[k] = v
        return settings

    def get_options(self, settings):
        """Get command line options."""
        options = []
        for name, value in settings.items():
            if name in self.plugin_options:
                continue
            if not option_name_re.match(name):
                msg = "isorted: settings names not properly configured."
                sublime.error_message(msg)
                raise Exception(msg)
            # We only support long arguments, no single dash arguments
            option = "--%s" % name.replace("_", "-")
            if isinstance(value, bool) and value:
                options.append(option)
            elif isinstance(value, list) and all(isinstance(v, (str, int, float)) for v in value):
                options.extend(itertools.product([option], map(str, value)))
            elif isinstance(value, (str, int, float)):
                options.extend([option, str(value)])
            else:
                msg = "isorted: only boolean, strings, numbers and list of strings and numbers allowed in settings."
                sublime.error_message(msg)
                raise Exception(msg)
        return options

    @property
    def encoding(self):
        """Get current file encoding."""
        encoding = self.view.encoding()
        if encoding == "Undefined":
            encoding = sublime.load_settings("Preferences.sublime-settings").get("default_encoding")
        if not encoding:
            region = self.view.line(sublime.Region(0))
            for shift in range(1):
                region = self.view.line(region.end() + shift)
                encoding = encoding_re.findall(self.view.substr(region))
                if encoding:
                    encoding = encoding[0]
                    break
            else:
                encoding = "utf-8"
        return encoding.lower()


class IsortedOnSave(sublime_plugin.ViewEventListener):
    """isorted listener class."""

    def on_pre_save(self):
        """File on save callback."""
        if self.isort_on_save:
            self.view.run_command("isort_file")
        return True

    @property
    def isort_on_save(self):
        """Check isort_on_save setting."""
        settings = self.view.settings()
        return bool(
            settings.get("isorted.isort_on_save")
            or settings.get("isorted", {}).get("isort_on_save", False)
            or sublime.load_settings("isorted.sublime-settings").get("isort_on_save")
        )
