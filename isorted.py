"""isorted plugin."""
import itertools
import os
import re
import subprocess

import sublime
import sublime_plugin

encoding_re = re.compile(r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")
name_re = re.compile(r"^(:?[a-z]{1,2}|[a-z][a-z_]+[a-z])$")


class IsortFileCommand(sublime_plugin.TextCommand):
    """isort_file command class."""

    def is_enabled(self):
        """Check file is python."""
        return self.view.match_selector(0, "source.python")

    is_visible = is_enabled

    def get_settings(self):
        """Get plugin settings."""
        # Get settings from plugin settings file
        settings = sublime.load_settings("isorted.sublime-settings").to_dict()  # I know it's slow...
        try:
            # Get project settings
            project_settings = self.view.window().project_data()["settings"]
            for name, value in project_settings.items():
                if name.startswith("isorted.") and len(name) > 8:
                    settings[name[8:]] = value
                elif name == "isorted":
                    for k, v in value.items():
                        settings[k] = v
        except (AttributeError, KeyError):
            pass
        return settings

    def get_options(self, settings):
        """Get options."""
        options = []
        for name, value in settings.items():
            if name in ("isort_command", "isort_on_save"):
                continue
            if not isinstance(name, str) or not name_re.match(name):
                msg = "Settings names not properly configured. Problem with settings?"
                sublime.error_message(msg)
                raise Exception(msg)
            # We only support long arguments, no single dash arguments
            option = "--%s" % name.replace("_", "-")
            if option and value:
                if isinstance(value, bool) and value:
                    options.append(option)
                elif isinstance(value, list) and all(isinstance(v, (str, int, float)) for v in value):
                    options.extend(itertools.product([option], map(str, value)))
                elif isinstance(value, (str, int, float)):
                    options.extend([option, str(value)])
                else:
                    msg = "Only boolean, strings, numbers and list of strings and numbers allowed. Problem with settings?"
                    sublime.error_message(msg)
                    raise Exception(msg)
        return options

    def get_command_line(self):
        """Get command line for isort."""
        settings = self.get_settings()
        try:
            cmd = settings["isort_command"]
            assert cmd and (isinstance(cmd, str) or isinstance(cmd, list) and all(isinstance(c, str) for c in cmd))
        except (KeyError, AssertionError) as e:
            msg = "'isort_command' not properly configured. Problem with settings?"
            sublime.error_message(msg)
            raise Exception(msg) from e
        if isinstance(cmd, str):
            cmd = [cmd]
        window_context = self.view.window().extract_variables()
        cmd = [sublime.expand_variables(os.path.expanduser(c), window_context) for c in cmd]
        options = self.get_options(settings)
        cmd.extend(options)
        cmd.append("-")  # set isort in input/ouput mode with -
        return cmd

    def get_good_working_dir(self):
        """Get good working directory for isort."""
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

    def windows_popen_prepare(self):
        """Prepare popen for Windows."""
        # win32: hide console window
        if sublime.platform() == "windows":
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startup_info.wShowWindow = subprocess.SW_HIDE
        else:
            startup_info = None
        return startup_info

    def get_encoding(self):
        """Get current file encoding."""
        region = self.view.line(sublime.Region(0))
        encoding = encoding_re.findall(self.view.substr(region))
        if encoding:
            return encoding[0]
        else:
            region = self.view.line(region.end() + 1)
            encoding = encoding_re.findall(self.view.substr(region))
            if encoding:
                return encoding[0]
        return "utf-8"

    def run(self, edit):
        """Run plugin."""
        current_positions = list(self.view.sel())
        this_contents = self.view.substr(sublime.Region(0, self.view.size()))
        cmd = self.get_command_line()
        encoding = self.get_encoding()
        try:
            p = subprocess.Popen(
                cmd,
                cwd=self.get_good_working_dir(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=self.windows_popen_prepare(),
            )
            out, err = p.communicate(input=this_contents.encode(encoding), timeout=10)
        except (UnboundLocalError, OSError) as e:
            msg = "You may need to install isort and/or configure 'isort_command' in isorted's settings."
            sublime.error_message("%s: %s\n\n%s" % (e.__class__.__name__, e, msg))
            raise Exception(msg)

        if not p.returncode and not err:
            self.view.replace(edit, sublime.Region(0, self.view.size()), out.decode(encoding))
            # Our sel has moved now...
            remove_sel = self.view.sel()[0]
            self.view.sel().subtract(remove_sel)
            for pos in current_positions:
                self.view.sel().add(pos)


class IsortedOnSave(sublime_plugin.ViewEventListener):
    """isorted listener class."""

    def on_pre_save(self):
        """File on save callback."""
        if self.isort_on_save:
            self.view.run_command("isort_file")

    @property
    def isort_on_save(self):
        """Check isort_on_save setting."""
        settings = self.view.settings()
        try:
            return bool(settings.get("isorted.isort_on_save"))
        except KeyError:
            pass
        try:
            return bool(settings.get("isorted")["isort_on_save"])
        except KeyError:
            pass
        settings = sublime.load_settings("isorted.sublime-settings")
        return bool(settings.get("isort_on_save"))
