"""isorted plugin."""
import os
import re
import subprocess

import sublime
import sublime_plugin

encoding_re = re.compile(r"^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)")


def get_setting(self, name):
    """Get plugin settings."""
    defaults = sublime.load_settings("isorted.sublime-settings")
    settings = self.view.settings().to_dict()
    return settings.get(f"isorted.{name}", settings.get("isorted", {}).get(name, defaults.get(name)))


class IsortFileCommand(sublime_plugin.TextCommand):
    """isort_file command class."""

    def is_enabled(self):
        """Check file is python."""
        return self.view.match_selector(0, "source.python")

    is_visible = is_enabled

    def expand_command_variables(self, cmd):
        cmd = os.path.expanduser(cmd)
        return sublime.expand_variables(cmd, self.view.window().extract_variables())

    def get_command_line(self):
        """Get command line for isort."""
        try:
            cmd = get_setting(self, "isort_command")
            assert cmd
        except (KeyError, AssertionError) as e:
            msg = "'isort_command' not configured. Problem with settings?"
            sublime.error_message(msg)
            raise Exception(msg) from e
        if isinstance(cmd, list):
            cmd = [self.expand_command_variables(c) for c in cmd]
            cmd.append("-")  # set isort in input/ouput mode with -
            return cmd
        cmd = self.expand_command_variables(cmd)
        return [cmd, "-"]  # set isort in input/ouput mode with -

    def get_good_working_dir(self):
        """Get good workin directory for isort."""
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
        """Get current file encodign."""
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
                shell=isinstance(cmd, str) and " " in cmd,
                cwd=self.get_good_working_dir(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=self.windows_popen_prepare(),
            )
            out, err = p.communicate(input=this_contents.encode(encoding))
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
        isort_on_save = get_setting(self, "isort_on_save")
        if isort_on_save:
            self.view.run_command("isort_file")
