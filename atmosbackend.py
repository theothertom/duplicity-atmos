# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os.path
import urllib

import duplicity.backend
from duplicity import globals
from duplicity import log
from duplicity.errors import * #@UnusedWildImport
from duplicity import tempdir
from EsuRestApi import EsuRestApi
from ConfigParser import SafeConfigParser

class AtmosBackend(duplicity.backend.Backend):
    """Connect to remote store using File Transfer Protocol"""
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)

        self.parsed_url = parsed_url
        #URL string: atmos://host/path/ 
        self.url_string = duplicity.backend.strip_auth_from_url(self.parsed_url)
        self.url_path   = '/' + '/'.join(self.url_string.split('/')[3:])
        host            = self.url_string.split('/')[2].split(':')[0]
        #Hacks
        try:
            port        = self.url_string.split('/')[2].split(':')[1]
        except Exception:
            port=443
            pass
        parser = SafeConfigParser()
        parser.read('/etc/duplicity/atmos.ini')
        uid=parser.get(host, 'uid')
        secret=parser.get(host, 'secret')
        log.Debug("Parsed URL:" + self.url_string)

        #Init Atmos connection
        self.api = EsuRestApi( host, int(port), uid, secret )

        # Use an explicit directory name.
        if self.url_string[-1] != '/':
            self.url_string += '/'

    def put(self, source_path, remote_filename = None):
        """Transfer source_path to remote_filename"""
        if not remote_filename:
            remote_filename = source_path.get_filename()
        remote_path = self.url_path + '/' + remote_filename 
        log.Debug("Upload " + source_path.get_filename() + " to " + remote_path)
        object_id = self.api.create_object_on_path(remote_path, None, None, None, None, open(source_path.name).read())

    def get(self, remote_filename, local_path):
        """Get remote filename, saving it to local_path"""
        remote_path = os.path.join(urllib.unquote(self.parsed_url.path), remote_filename).rstrip()
        log.Debug("Download " + remote_filename + " to " + local_path.name)
        f = open(local_path.name, 'w')
        f.write(self.api.read_object_from_path(self.url_path + '/' + remote_filename))
        f.close()

    def list(self):
        """List files in directory"""
        # Do a long listing to avoid connection reset
        log.Debug("Listing " + self.url_path)
        listing = []
        try:
            for file in self.api.list_directory(self.url_path)[0]:
                log.Debug("Found: " + file[2])
                listing.append (file[2])
        except Exception:
            #The library will fail with EsuException: EsuException when remote folder doesn't exist
            pass
        return listing

    def delete(self, filename_list):
        """Delete files in filename_list"""
        for filename in filename_list:
            filename=self.url_path + '/' + filename
            for fileinfo in self.api.list_directory(os.path.dirname(filename))[0]:
                if fileinfo[2] == os.path.basename(filename):
                    file_id = fileinfo[0]
                    break
            log.Debug("Delete " + filename + "(ID: " + file_id + ")")
            self.api.delete_object(file_id)

duplicity.backend.register_backend("atmos", AtmosBackend)
