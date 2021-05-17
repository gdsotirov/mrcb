2021-06-?? _2021.06_
------------------------------------------------------------------------------
* _Change_: Reuse SFTP connection for downloading files (see
  [#6](https://github.com/gdsotirov/mrcb/issues/6);

2021-05-16 _2021.05_
------------------------------------------------------------------------------
* _New_: Make binary backups and preserve only the one from the last
  configuration change (see [#4](https://github.com/gdsotirov/mrcb/issues/4));
* _New_: Unique names for backup and export files on device and cleanup after
  download (see [#5](https://github.com/gdsotirov/mrcb/issues/5)).
* _Change_: Use [colorama](https://pypi.org/project/colorama/) for colored
  output on terminal.

2020-03-02 _2020.03_
------------------------------------------------------------------------------
* _New_: JSON schema definition and validation for the configuration (see
  [#3](https://github.com/gdsotirov/mrcb/issues/3)).

2020-02-29 _2020.02_
------------------------------------------------------------------------------
* Initial public release featuring:
  - configuration of devices in JSON;
  - SSH connection to devices with password;
  - generation of configuration export, download and comparison with previous
    export to determine whether to keep it or not;
  - backup export in per device directory (see
    [#1](https://github.com/gdsotirov/mrcb/issues/1) and
    [#2](https://github.com/gdsotirov/mrcb/issues/2)).

