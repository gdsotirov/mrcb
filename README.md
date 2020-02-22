# Multi Router Configuration Backup (MRCB)

Multi Router Configuration Backup is a utility to backup the configuration
of multiple MikroTik devices on the network on a regular basis by keeping
new configuration only if it differs from the last one.

MRCB connects to remote MikroTik devices by SSH, executes command to generate
export file and then retrieves this file by SFTP.

# Requirements

The utility requires Python 2 and [Paramiko](http://www.paramiko.org/) module.

# License

The utility is licensed under MIT license. For details please see LICENSE.

