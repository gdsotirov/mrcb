#!/usr/bin/env python
#
# Multi Router Configuration Backup (MRCB)
# Copyright (c) 2020-2021 Georgi D. Sotirov
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

import datetime, glob, json, jsonschema, os, sys
import error as e, routeros

# Default configuration file location
MRCB_CONFIG = "config.json"
# Default backup directory
DEF_BACKUPDIR = './backup'
# Return error codes
ERR_NO_ERROR            = 0
ERR_CANNOT_OPEN_CONFIG  = 1
ERR_CANNOT_PARSE_CONFIG = 2
ERR_CANNOT_VAL_CONFIG   = 3
ERR_CANNOT_CREATE_DIR   = 4
ERR_NOT_A_DIR           = 5

def get_latest_export(bkp_dir, per_device, dev_name):
  "Get name of latest export file by modification time"
  if per_device:
    glob_pattern = "%s/%s/%s_*.rsc" % (bkp_dir, dev_name, dev_name)
  else:
    glob_pattern = "%s/%s_*.rsc" % (bkp_dir, dev_name)

  files = glob.glob(glob_pattern)

  if files:
    # TODO: What if old export was changed recently?
    return max(files, key=os.path.getmtime)
  else:
    return ''

def load_and_check_config(cfg_file):
  "Loads and validates configuration, uses defaults where possible"
  # Open configuration file
  try:
    cfg_file = open(cfg_file, "r")
  except Exception as err:
    e.perror("Cannot open configuration file '%s': %s" % (MRCB_CONFIG, str(err)))
    return ERR_CANNOT_OPEN_CONFIG, None

  # Load configuration
  try:
    cfg = json.load(cfg_file)
  except Exception as err:
    e.perror("Cannot parse configuration: %s" % str(err))
    return ERR_CANNOT_PARSE_CONFIG, None

  cfg_file.close()

  # Validate configuration against JSON schema
  try:
    with open("config.schema.json", "r") as cfg_schema_file:
      cfg_schema = json.load(cfg_schema_file)
      jsonschema.validate(cfg, cfg_schema)
      cfg_schema_file.close()
  except Exception as err:
    e.perror("Cannot validate configuration: %s" % str(err))
    return ERR_CANNOT_VAL_CONFIG, None

  # Set values of optional configuration properties
  if not cfg.get('backup_dir'):
    e.pwarn("Using default backup directory '%s'. Please, check your configuration." % DEF_BACKUPDIR)
    cfg['backup_dir'] = DEF_BACKUPDIR

  if not cfg.get('backup_dir_per_device'):
    cfg['backup_dir_per_device'] = True

  return ERR_NO_ERROR, cfg

def main():
  res, cfg = load_and_check_config(MRCB_CONFIG)
  if ( res != ERR_NO_ERROR ):
    return res

  # Check if backup directory exist and try to create it
  if not os.path.exists(cfg['backup_dir']):
    try:
      e.pinfo("Creating directory '%s'." % cfg['backup_dir'])
      os.mkdir(cfg['backup_dir'])
    except Exception as err:
      e.perror("Cannot create backup directory '%s': %s" % (cfg['backup_dir'], str(err)))
      return ERR_CANNOT_CREATE_DIR
  elif not os.path.isdir(cfg['backup_dir']):
    e.perror("Path '%s' set as 'backup_dir' is not a directory!" % cfg['backup_dir'])
    return ERR_NOT_A_DIR

  # Loop routers
  for rtr in cfg['routers']:
    old_backups = []

    e.pinfos("Backing up '%s'... " % rtr['name'])

    # export configuration
    try:
      ros = routeros.SecureTransport(rtr['hostname'], rtr['port'])

      try:
        login_pass = rtr['password']
      except KeyError as err:
        login_pass = None
        try:
          priv_key_f = rtr['priv_key']
        except KeyError as err:
          priv_key_f = None

      ros.login(rtr['username'], login_pass, priv_key_f)
      ros.make_backup()
      ros.make_export()
      today = datetime.datetime.now()
      today_str = today.strftime("%Y%m%d-%H%M%S")

      if cfg['backup_dir_per_device']:
        dev_bkp_dir = "%s/%s" % (cfg['backup_dir'], rtr['name'])
        if not os.path.exists(dev_bkp_dir):
          try:
            os.mkdir(dev_bkp_dir)
          except Exception as err:
            e.perror("Cannot create device backup directory '%s': %s" % (dev_bkp_dir, str(err)))
            continue
        local_bkp_file = "%s/%s/%s_%s.backup" % (cfg['backup_dir'], rtr['name'], rtr['name'], today_str)
        local_exp_file = "%s/%s/%s_%s.rsc" % (cfg['backup_dir'], rtr['name'], rtr['name'], today_str)
      else:
        local_bkp_file = "%s/%s_%s.backup" % (cfg['backup_dir'], rtr['name'], today_str)
        local_exp_file = "%s/%s_%s.rsc" % (cfg['backup_dir'], rtr['name'], today_str)

      # get last export before new one is downloaded
      last_exp_file = get_latest_export(cfg['backup_dir'],
                                        cfg['backup_dir_per_device'],
                                        rtr['name'])

      # TODO: Get remote file datetime?
      ros.get_backup(local_bkp_file)
      ros.get_export(local_exp_file)
      ros.cleanup()
      ros.close()
    except Exception as err:
      e.pinfoe("Fail.")
      e.perror("Cannot get configuration: %s" % str(err))
      continue

    for bkp_file in os.listdir(dev_bkp_dir):
      if bkp_file.endswith(".backup"):
        if ( os.path.join(dev_bkp_dir, bkp_file) != local_bkp_file ):
          old_backups.append(os.path.join(dev_bkp_dir, bkp_file))

    # compare with last configuration export if any
    if last_exp_file:
      ros_exp = routeros.Export()
      if ros_exp.same(last_exp_file, local_exp_file):
        e.pinfoe("Kept (as '%s' is same)." % os.path.basename(last_exp_file))
        if len(old_backups) > 0:
          os.remove(local_bkp_file)
        os.remove(local_exp_file)
      else:
        e.pinfoe("Done (as '%s' is different from '%s')." %
          (os.path.basename(local_exp_file), os.path.basename(last_exp_file)))
    else:
      e.pinfoe("Done (as '%s' is initial)." % os.path.basename(local_exp_file))

    # clean up old system backups
    if os.path.exists(local_bkp_file) and os.path.isfile(local_bkp_file):
      for old_bkp_file in old_backups:
        os.remove(old_bkp_file)

exit(main())

