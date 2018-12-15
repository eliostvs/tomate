Tomate
======

A pomodoro timer written in Python. This project has only the core classes.
[Here][1] is the repository of the Gtk version.

Bugs and Suggestions
--------------------

Bugs and suggestions should be reported [here][2].

Change Logs
-----------

### 0.9.0

#### Changed

- Rename domain class **Task** to **Session**
- Keep in memory all past sessions instead of only the count of pomodoros 

### 0.8.0

#### Added

- **show\_message** method to view interface

#### Fix

- Values with space in settings (ex: alarm file path)

### 0.7.0

- Using wiring.scanning
- Add plugin settings
- Python 3 only (packages)

### 0.6.0

- Using py.test
- Skip supress\_error decorator with environment variable
- Add rounded\_percent function
- Add lazy proxy function

### 0.5.0

- Remove linux package metadata

### 0.4.0

- Create a new event system
- Python 2/3 compatible

License
-------

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License version 3, as published
by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranties of
MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

[1]: https://github.com/eliostvs/tomate-gtk
[2]: https://github.com/eliostvs/tomate/issues
