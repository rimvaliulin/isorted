=======
Isorted
=======

`isort`_ integration for Sublime Text

* License : GNU General Public License v3 or later (GPLv3+)
* Source: https://github.com/rimvaliulin/isorted.git

::

       __
      / /               __           __
     / /________  _____/ /____  ____/ /
    / / ___/ __ \/ ___/ __/ _ \/ __  /
   / /__  / /_/ / /  / /_/  __/ /_/ /
  /_/____/\____/_/   \__/\___/\__,_/



Table Of content
----------------

`Installation`_ | `Usage`_  |  `Settings`_ | `Issues`_ | `Thanks`_ | `Changelog`_ | `Contributing`_ | `Authors`_


Installation
------------

#. Install `isort`_ min (19.3b0) (if you haven't already)

::

  pip3 install isort # Requires python 3.6

#. In PackageControl just find ``isort``, and that's it!

or

Without PackageControl install manually by navigating to Sublime's `Packages` folder and cloning this repository

::

  git clone https://github.com/rimvaliulin/isorted.git


Usage
-----

* Run isort on the current file:
    Press `Ctrl-Alt-S` (Mac: `Cmd-Alt-S`) to sort importd in the entire file.
    You can also `Ctrl-Shift-P` (Mac: `Cmd-Shift-P`) and select `Isorted: Format file`.


Settings
--------

isort will always look for settings in the following order:
 - First in a .isort.cfg file
 - Second in the pyproject.toml.
 - Then setup.cfg, tox.ini, .editorconfig

See: https://pycqa.github.io/isort/docs/configuration/config_files.html


Global settings
***************
Preferences -> Package Settings -> Isorted -> settings :


Isorted specifics options
+++++++++++++++++++++++++

* isort_command:
    Set custom location. Default = "isort".

* isort_on_save:
    Black is always run before saving the file. Default = false.


Project settings
****************

Just add isorted as prefix (recommended):

.. code-block:: json

  {
      "settings": {
          "isorted.isort_on_save": true
      }
  }

A isorted subsettings is still possible:

.. code-block:: json

  {
      "settings": {
          "isorted": {
              "isort_on_save": true
          }
      }
  }


Issues
------

If there is something wrong with this plugin, `add an issue <https://github.com/rimvaliulin/isorted/issues>`_ on GitHub and I'll try to address it.


Thanks
------
This plugin is very inspired by `Sublime text isort plugin <https://github.com/thijsdezoete/sublime-text-isort-plugin>`_ and `Sublack <https://github.com/jgirardet/sublack>`_ Plugin. Thanks to Thijs de Zoute and Jimmy Girardet.


Changelog
---------

see `CHANGELOG <CHANGELOG>`_


Contributing
------------

* Remove isorted via Package Control.
* Fork isorted
* Clone your isorted fork to your Packages folder (Preferences -> Browse Packages...).
* Add your name to Authors in the readme.


Authors
-------

Coded by Rim Valiulin

Contributions by:

* ...

Todo
----

- ...

.. _isort : https://github.com/PyCQA/isort
