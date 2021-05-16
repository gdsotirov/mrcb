# Multi Router Configuration Backup (MRCB)

Multi Router Configuration Backup is a utility to back up the configuration
of multiple MikroTik devices on the network in the form of:
  * [system backup](https://wiki.mikrotik.com/wiki/Manual:System/Backup)
  (binary file); and
  * [configuration export](https://wiki.mikrotik.com/wiki/Manual:Configuration_Management)
  (plain text file without secrets).

It is intended to be run on a regular basis. New configuration backups are kept
only if new export differs from the last one that was preserved in the same way.

## How does it work?

MRCB connects to remote MikroTik devices via SSH and executes the necessary
commands to generate system backup (`mrcb_#######.backup`) and configuration
export (`mrcb_#######.rsc`) files (where `#` is random lowercase or uppercase
ASCII letter or digit). It then retrieves these files by SFTP and compares
the new export with the last backed up version excluding comments (i.e. lines
beginning with `#`). If exports are the same the new backup and export files
are deleted preserving disk space and keeping history of changes clean.
Otherwise, the new export and backup are preserved for reference and quick
restore, respectively.

# Requirements

The utility requires:
  * [Python](https://www.python.org/) 2.7 or later;
  * [Paramiko](https://www.paramiko.org/) 2.3 or later;
  * [colorama](https://github.com/tartley/colorama) 0.3.9 or later;
  * [jsonschema](https://github.com/Julian/jsonschema) 2.6 or later.

# License

This software is licensed under MIT license. Please, see file [LICENSE](LICENSE).

