# Multi Router Configuration Backup (MRCB)
# Module for secure interaction with RouterOS devices
# Copyright (c) 2020 Georgi D. Sotirov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import paramiko, time

class SecureTransport:
  "SSH/SFTP to RouterOS device"

  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.pt = paramiko.Transport((self.host, self.port))

  def login(self, user, passwd):
    "SSH login"
    self.pt.connect(username = user, password = passwd)

  def export(self):
    "Execute command to create export file"
    self.ssh = self.pt.open_session()
    self.ssh.exec_command('/export file=today hide-sensitive compact')
    # wait for the export command to complete
    while True:
      if self.ssh.exit_status_ready():
        break
      time.sleep(1)

  def get_export(self, local_file):
    "Get remote file into local file"
    self.sftp = self.pt.open_sftp_client()
    self.sftp.get('/today.rsc', local_file)

  def close(self):
    "Close transport"
    self.pt.close()

