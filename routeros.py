# Multi Router Configuration Backup (MRCB)
# Module for secure interaction with RouterOS devices
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

import paramiko, re, time

class SecureTransport:
  "SSH/SFTP to RouterOS device"

  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.pt = paramiko.Transport((self.host, self.port))

  def close(self):
    "Close transport"
    self.pt.close()

  def get_backup(self, local_file):
    "Get system backup file"
    self.get_file('today.backup', local_file)

  def get_export(self, local_file):
    "Get export file"
    self.get_file('today.rsc', local_file)

  def get_file(self, remote_file, local_file):
    "Get remote file into local file"
    self.sftp = self.pt.open_sftp_client()
    self.sftp.get(remote_file, local_file)

  def login(self, user, passwd):
    "SSH login"
    self.pt.connect(username = user, password = passwd)

  def make_backup(self):
    "Execute command to create backup file"
    self.ssh = self.pt.open_session()
    # See https://help.mikrotik.com/docs/display/ROS/Backup
    self.ssh.exec_command('/system backup save name=today.backup')
    # wait for the backup command to complete
    while True:
      if self.ssh.exit_status_ready():
        break
      time.sleep(1)

  def make_export(self):
    "Execute command to create export file"
    self.ssh = self.pt.open_session()
    # Export only non-default configuration and hide secrets (i.e. passwords)
    # See https://wiki.mikrotik.com/wiki/Manual:Configuration_Management
    self.ssh.exec_command('/export file=today hide-sensitive compact')
    # wait for the export command to complete
    while True:
      if self.ssh.exit_status_ready():
        break
      time.sleep(1)

class Export:
  "Export handling routines"

  def same(self, old_exp, new_exp):
    "Compare whether two exports are the same"
    oldexp = open(old_exp)
    newexp = open(new_exp)

    for old_exp_ln, new_exp_ln in zip(oldexp, newexp):
      if self.skip_ln(old_exp_ln) or self.skip_ln(new_exp_ln):
        continue
      elif old_exp_ln != new_exp_ln:
        oldexp.close()
        newexp.close()
        return False

    oldexp.close()
    newexp.close()

    return True

  def skip_ln(self, line):
    "Lines to skip from export"
    if re.search("^#", line):
      return True # skip comments

    return False

