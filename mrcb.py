#!/usr/bin/env python
#
# Multi Router Configuration Backup (MRCB)
# Copyright (c) 2020 Georgi D. Sotirov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import datetime, json, os, sys
import error as e, routeros

# Default configuration file location
MRCB_CONFIG = "config.json"
# Default backup directory
DEF_BACKUPDIR = './backup'

def main():
  # Open configuration file
  try:
    cfg_file = open(MRCB_CONFIG, "r")
  except Exception as err:
    e.perror("Error: Cannot open configuration file '%s': %s" % (MRCB_CONFIG, str(err)))
    return 1

  # Load configuration
  try:
    cfg = json.load(cfg_file)
  except Exception as err:
    e.perror("Error: Cannot read configuration: %s" % str(err))
    return 2

  cfg_file.close()

  if not cfg.get('backup_dir'):
    e.pinfo("Warning: Using default backup directory '%s'. Please, check your configuration." % DEF_BACKUPDIR)
    cfg['backup_dir'] = DEF_BACKUPDIR

  # Check if backup directory exist and try to create it
  if not os.path.exists(cfg['backup_dir']):
    try:
      e.pinfo("Info: Creating directory '%s'." % cfg['backup_dir'])
      os.mkdir(cfg['backup_dir'])
    except Exception as err:
      e.perror("Error: Cannot create backup directory '%s': %s" % (cfg['backup_dir'], str(err)))
      return 3
  elif not os.path.isdir(cfg['backup_dir']):
    e.perror("Error: Path '%s' set as 'backup_dir' is not a directory!" % cfg['backup_dir'])
    return 4

  if not cfg.get('routers'):
    e.perror("Error: No routers configured! Please, fix your configuration.")
    return 5

  # Loop routers and dump configuration
  for rtr in cfg['routers']:
    e.pinfoc("Info: Backing up configuration of '%s'... " % rtr['name'])

    try:
      ros = routeros.SecureTransport(rtr['hostname'], rtr['port'])
      ros.login(rtr['username'], rtr['password'])
      ros.make_export()
      today = datetime.datetime.now()
      today_str = today.strftime("%Y%m%d-%H%M%S")
      local_exp_file = cfg['backup_dir'] + "/" + rtr['name'] + "_" + today_str + ".rsc"
      # TODO: Get remote file datetime?
      ros.get_export(local_exp_file)
      ros.close()
    except Exception as err:
      e.pinfo("Fail.")
      e.perror("Error: Cannot get configuration: %s" % str(err))
      continue

    e.pinfo("Done.")

exit(main())

