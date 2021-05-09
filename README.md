# Multi Router Configuration Backup (MRCB)

Multi Router Configuration Backup is a utility to backup the configuration
of multiple MikroTik devices on the network on a regular basis by keeping
new configuration only if it differs from the last one.

## How does it work?

MRCB connects to remote MikroTik devices by SSH, executes command to generate
export file and then retrieves this file by SFTP. It then compares the new
export with the last backed up version excluding comments (i.e lines beginning
with `#`). If exports are the same the new one is deleted preserving space and
keeping history. Otherwise, the new version is preserved for reference.

# Requirements

The utility requires:
  * [Python](https://www.python.org/) 2.7 or later;
  * [Paramiko](https://www.paramiko.org/) 2.3 or later;
  * [colorama](https://github.com/tartley/colorama) 0.3.9 or later;
  * [jsonschema](https://github.com/Julian/jsonschema) 2.6 or later;

# License

This software is licensed under MIT license. Please, see file [LICENSE](LICENSE).

