# Multi Router Configuration Backup (MRCB)

Multi Router Configuration Backup is a utility to backup the configuration
of multiple MikroTik devices on the network on a regular basis by keeping
new configuration only if it differs from the last one.

MRCB connects to remote MikroTik devices by SSH, executes command to generate
export file and then retrieves this file by SFTP.

# Requirements

The utility requires:
  * [Python](https://www.python.org/) 2.7 or later;
  * [Paramiko](https://www.paramiko.org/) 2.3 or later.

# License

This software is licensed under MIT license. Please, see file [LICENSE](LICENSE).

