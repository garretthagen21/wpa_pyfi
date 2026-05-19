Changelog
=========

0.5.4
^^^^^
:release-date: 2026-05-19

- ``Network.save()`` now calls ``delete(disconnect_immediately=False)`` when overwriting an
  existing entry, preventing spurious ``wpa_cli reconfigure`` calls during
  ``reconfigure_priority()`` that caused wpa_supplicant to revert to the previously
  connected network.
- ``Network.activate()`` now calls ``wpa_cli reassociate`` after reconfiguring, forcing
  wpa_supplicant to drop the current connection and reconnect to the highest-priority network.

0.5.3
^^^^^
:release-date: 2026-05-19

- ``Cell.all()`` accepts a ``scan_method`` parameter (``'iwlist'`` or ``'wpa_cli'``).
  The ``'wpa_cli'`` path uses ``wpa_cli scan`` + ``wpa_cli scan_results`` instead of
  ``/sbin/iwlist``, avoiding conflicts with wpa_supplicant during active association.
- ``Network.activate()`` now returns the ``wpa_cli`` output string on success instead of
  ``None``, allowing callers to verify the reconfigure succeeded.

0.5.2
^^^^^
:release-date: 2021-02-10

- There was an issue in 0.5.1 that prevented pip install. PyPi will not let me overwrite/remove it so it is being fixed in this release

0.5.1
^^^^^
:release-date: 2021-02-03

- Add automatic priority management so activated networks will connect (fix ambiguity bug)
- Remove explicit priority specification on network creation
- Fix parsing bug that would cause connection data retrieval to fail for network
- Make NETNAME parameter optional in CLI arguments

0.5.0
^^^^^
:release-date: 2021-01-04

- Packaged renamed from wifi to wpa_pyfi
- Project was rebuilt to run on wpa_cli instead of ifup and ifdown (a noteable issue for RPi Users)
- Scheme class was replaced with Network class
- Configurations are saved by default in /etc/wpa_supplicant/wpa_supplicant.conf instead of /etc/networks/interfaces (previous)
- Ad hoc network connection via CLI is no longer supported
- Connection class is no longer utilized. IfConfigParser object is used instead to view connection information
- Network tests are currently broken
- Discontinued support for Python3

0.4.0
^^^^^
:release-date: unknown

- Make the wifi command name configurable (#55 - thanks yourealwaysbe)
- Add a __main__.py so that wifi can be invoked using python -mwifi
- Fix argument parsing so that scan is the default argument even with options passed

0.3.8
^^^^^
:release-date: 2016-03-11

- Parse noise level if available (#91 - thanks zgoda-mobica)

0.3.7
^^^^^
:release-date: 2016-03-11

- Fix bugs related to scheme parsing (#59, #42)

0.3.6
^^^^^
:release-date: 2016-02-11

- Set all attributes to None in Cell.__init__ (#88 - thanks stvad)

0.3.5
^^^^^
:release-date: 2016-01-24

- Better password handling (#62 - thanks foosel)
- Account for Cells with no SSID (#86 - thanks tlau)

0.3.4
^^^^^
:release-date: 2014-09-02

- Fixed installation missing some files (#48 - thanks luckydonald)

0.3.3
^^^^^
:release-date: 2014-08-31

- Check for write access for bashcompletion via os.access (#41, #47 - thanks foosel and jegger)
- Fixed scanning when quality is reported absolutely (#45 - jeromelebel)
- Fixed channel parsing (#33, #39 - thanks gavinwahl and qizha)

0.3.2
^^^^^
:release-date: 2014-07-26

- Only run if __name__ == '__main__' (#29 - thanks Jonwei)
- Try to connect to the nearest Access Point
- wifi scan was failing when Bit Rate was the last line of output (#42 - thanks jargij)
- Added documentation for signal and quality on Cell

0.3.1
^^^^^
:release-date: 2014-02-10

- Scheme.activate was failing on a TypeError in Python3

0.3.0
^^^^^
:release-date: 2014-02-09

- Scheme.activate now throws a ConnectionError if activation failed (#17 - thanks alexykot)
- Cell.all now throws an InterfaceError if scanning failed (#18 - thanks alexykot)
- Better error message when scheme isn't found (#19 - thanks gavinwahl)
- Added ability to delete schemes (#20 - thanks spektom)
- Added the --file option (#21)
- Scheme.activate returns a Connection object (#22)
- Added the autoconnect command (#23)
- Fixed parsing error missing channel (#24 - thanks LiorKirsch)
- Fixed relative signal return as zero (#25 - thanks LiorKirsch)
- Relative signals are now converted to dBm (#26 - thanks LiorKirsch)
- Various codebase cleanup (#27 - thanks ramnes)
- Added support for WPA Version 1 (#28 - thanks LiorKirsch)
- Fixed Python3 support for WPA/PBKDF2

0.2.2
^^^^^
:release-date: 2013-12-25

- Fixed relative signal parsing bug (#12 - thanks alexykot)

0.2.1
^^^^^
:release-date: 2013-11-22

- Fixed print_table str/int bug (#13 - thanks DanLipsitt)

0.2.0
^^^^^
:release-date: 2013-09-27

- Added support for WEP
- Fixed bug related to very short SSIDs
- Fixed bug related to numeric passkeys

0.1.1
^^^^^
:release-date: 2013-05-26

- Updated setup.py to actually install the bash completion script
