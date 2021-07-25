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

import paramiko, random, re, stat, string, time

class SecureTransport:
  "SSH/SFTP to RouterOS device"

  __RND_SEQ = string.ascii_uppercase + string.ascii_lowercase + string.digits

  def __init__(self, host, port):
    self.__rnd_fname = 'mrcb_' + ''.join(random.choice(self.__RND_SEQ) for _ in range(7))
    self.__bkp_fname = self.__rnd_fname + '.backup'
    self.__exp_fname = self.__rnd_fname + '.rsc'
    self.host = host
    self.port = port
    self.pt = paramiko.Transport((self.host, self.port))

  def cleanup(self):
    for file in [self.__bkp_fname, self.__exp_fname]:
      try:
        if stat.S_ISREG(self.sftp.stat(file).st_mode):
          self.sftp.remove(file)
      except IOError as e:
        if e.errno == 2 and e.strerror == "No such file or directory":
          pass

  def close(self):
    "Close transport"
    self.pt.close()

  def get_backup(self, local_file):
    "Get system backup file"
    self.get_file(self.__bkp_fname, local_file)

  def get_export(self, local_file):
    "Get export file"
    self.get_file(self.__exp_fname, local_file)

  def get_file(self, remote_file, local_file):
    "Get remote file into local file"
    try:
      self.sftp
    except AttributeError as e:
      self.sftp = self.pt.open_sftp_client()
    self.sftp.get(remote_file, local_file)

  def login(self, user, passwd, priv_key):
    "SSH login"
    if priv_key != None:
      key = paramiko.RSAKey.from_private_key_file(priv_key)
      self.pt.connect(username = user, pkey = key)
    elif passwd != None:
      self.pt.connect(username = user, password = passwd)
    else:
      raise Exception("No password or private key provided.")

  def make_backup(self):
    "Execute command to create backup file"
    self.ssh = self.pt.open_session()
    # See https://help.mikrotik.com/docs/display/ROS/Backup
    self.ssh.exec_command('/system backup save name=%s' % self.__bkp_fname)
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
    self.ssh.exec_command('/export file=%s hide-sensitive compact' % self.__exp_fname)
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

