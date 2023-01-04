isorted
=======

```
       __
      / /               __           __
     ---________  _____/ /____  ____/ /
    / / ___/ __ \/ ___/ __/ _ \/ __  /
   / /__  / /_/ / /  / /_/  __/ /_/ /
  /_/____/\____/_/   \__/\___/\__,_/
```

[`isort`](https://pycqa.github.io/isort/) integration for Sublime Text. Make your imports great again.

Allows to use any externally installed `isort` by your favorite package manager…

Installation
------------

Just find `isorted` in `Package Control` or install manually by navigating to Sublime's `Packages` folder and cloning this repository:

```bash
git clone https://github.com/rimvaliulin/isorted.git
```

Install `isort` if you haven't already:

```bash
  pip3 install isort
```

Configuration
-------------

### `isort` config files

`isort` looks for the closest supported config files in the order listed: `.isort.cfg`, `pyproject.toml`, `setup.cfg`, `tox.ini` and `.editorconfig` (`.isort.cfg` and `pyproject.toml` are preferred formats). `isort` will traverse up to 25 parent directories until it finds a suitable config file. `isort` will not leave a git or Mercurial repository (checking for a .git or .hg directory). As soon as it finds a file, it stops looking. The config file search is done relative to the current directory if `isort` or a file stream is passed in, or relative to the first path passed in if multiple paths are passed in. `isort` never merges config files together due to the confusion it can cause. You can manually specify the settings file or path by setting `--settings-path` from the command-line. See more: https://pycqa.github.io/isort/docs/configuration/config_files.html

### Project settings

Add a `isort` command line options to Sublime Text settings (see: `isort --help`). Use long arguments (double dashed) and change hyphens to underscores to better look. This settings will be added directly to command line call and override any `isort` config file settings: `.isort.cfg`, `pyproject.toml`, `setup.cfg`, `tox.ini`, `.editorconfig` etc.

Just add `isorted` as prefix:

```json
{
    "settings": {
        "isorted.isort_command": ["poetry", "run", "isort"],
        "isorted.isort_on_save": true,
        "isorted.profile": "black",
        "isorted.float_to_top": true,
        "isorted.line_length": 120
    }
}
```

Or in `isorted` subsettings:

```json
{
    "settings": {
        "isorted": {
            "isort_command": ["${python_interpreter}", "-m", "isort"],
            "isort_on_save": true,
            "profile": "django",
            "dont_float_to_top": true,
            "indent": "    ",
            "extra_builtin": ["django", "rest_framework"]
        }
    }
}
```
Or in `options` section of `isorted` subsettings:

```json
{
    "settings": {
        "isorted": {
            "isort_command": ["${python_interpreter}", "-m", "isort"],
            "isort_on_save": true,
            "options": {
                "profile": "django",
                "dont_float_to_top": true,
                "indent": "    ",
                "extra_builtin": ["django", "rest_framework"]
            }
        }
    }
}
```

### Global/User settings

`Preferences` → `Package Settings` → `isorted` → `Settings`

Fill user settings with options you like on the left panel:

```json
{
    "isort_command": "/usr/bin/local/isort",
    "isort_on_save": true,
    "options": {
        "profile": "pycharm",
        "multi_line": "GRID",
        "ensure_newline_before_comments": true,
        "known_local_folder": ["flask", "requests"]
    }
}
```

#### `isorted` specific options

- `isort_command`: set custom location for `isort` command. Can be list of strings (by default: "isort").

- `isort_on_save`: always run `isort` before saving the file (by default: false).


Key Bindings
------------

`Preferences` → `Package Settings` → `isorted` → `Key Bindings`:

Copy to user key bindings, uncomment, edit keys and and save:

```json
[
    {"keys": ["ctrl+alt+s"], "command": "isort_file", "scope": "source.python"}
]
```

Usage
-----

- Sort imports on save by `isort_on_save` settings.

- Open `Command Panel` from menu or with `ctrl+shift+p` (Mac: `cmd+shift+p`) and select `isorted: Format file`.

- Run `isort` on the current file with key bindings activated before:

  Press `ctrl+alt+s` (Mac: `cmd+alt+s`) to sort imports in the entire file.


Issues
------

If there is something wrong with this plugin, add an [issue](https://github.com/rimvaliulin/isorted/issues) on GitHub and I'll try to address it.


Thanks
------

This plugin is inspired by [Sublime text isort plugin](https://github.com/thijsdezoete/sublime-text-isort-plugin) and [sublack](https://github.com/jgirardet/sublack). Thanks to @thijsdezoete and @jgirardet.


Changelog
---------

see [CHANGELOG](CHANGELOG)


Contributing
------------

- Remove `isorted` via `Package Control`.
- Fork `isorted`
- Clone your `isorted` fork to your `Packages` folder (`Preferences` → `Browse Packages`…).
- Add your name to Authors in the readme.


Authors
-------

Coded by Rim Valiulin @rimvaliulin.

Contributions: Stanley Chung @returnchung.

Todo
----

- MacOS: Fix error 'You may need to install isort and/or configure 'isort_command' in isorted's settings.' on new Sublime Text startup after reboot (needs Sublime Text restart).

- Add quick toggle `isort_on_save` for specific file.

---

- License: [GNU General Public License v3 or later (GPLv3+)](LICENCE)
- Source: https://github.com/rimvaliulin/isorted.git

