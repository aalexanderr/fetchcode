# Copyright (c) 2008-2020 The pip developers:
# barneygale, Barney Gale, Chris Hunt, Chris Jerdonek, Christopher Hunt,
# Deepak Sharma, Devesh Kumar Singh, Donald Stufft, Dustin Ingram, Emil Burzo,
# Giftlin Rajaiah, Jason R. Coombs, Jelmer Vernooĳ, Jeremy Zafran, johnthagen,
# Jon Dufresne, Maxim Kurnikov, Nitesh Sharma, Pi Delport, Pradyun Gedam,
# Pradyun S. Gedam, Riccardo Magliocchetti, Shlomi Fish,
# Stéphane Bidoul (ACSONE), tbeswick, Tom Forbes, Tony Beswick, TonyBeswick,
# Tzu-ping Chung
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# The following comment should be removed at some point in the future.
# mypy: disallow-untyped-defs=False

from __future__ import absolute_import

import logging
import os

from urllib.parse import urlparse

from fetchcode.vcs.pip._internal.utils.misc import display_path, rmtree
from fetchcode.vcs.pip._internal.utils.subprocess import make_command
from fetchcode.vcs.pip._internal.utils.urls import path_to_url
from fetchcode.vcs.pip._internal.vcs.versioncontrol import VersionControl, vcs


logger = logging.getLogger(__name__)


class Bazaar(VersionControl):
    name = 'bzr'
    dirname = '.bzr'
    repo_name = 'branch'
    schemes = (
        'bzr', 'bzr+http', 'bzr+https', 'bzr+ssh', 'bzr+sftp', 'bzr+ftp',
        'bzr+lp',
    )

    def __init__(self, *args, **kwargs):
        super(Bazaar, self).__init__(*args, **kwargs)
        # Register lp but do not expose as a scheme to support bzr+lp.
        urlparse.uses_fragment.extend(['lp'])

    @staticmethod
    def get_base_rev_args(rev):
        return ['-r', rev]

    def export(self, location, url):
        # type: (str, HiddenText) -> None
        """
        Export the Bazaar repository at the url to the destination location
        """
        # Remove the location to make sure Bazaar can export it correctly
        if os.path.exists(location):
            rmtree(location)

        url, rev_options = self.get_url_rev_options(url)
        self.run_command(
            make_command('export', location, url, rev_options.to_args()),
            show_stdout=False,
        )

    def fetch_new(self, dest, url, rev_options):
        # type: (str, HiddenText, RevOptions) -> None
        rev_display = rev_options.to_display()
        logger.info(
            'Checking out %s%s to %s',
            url,
            rev_display,
            display_path(dest),
        )
        cmd_args = (
            make_command('branch', '-q', rev_options.to_args(), url, dest)
        )
        self.run_command(cmd_args)

    def switch(self, dest, url, rev_options):
        # type: (str, HiddenText, RevOptions) -> None
        self.run_command(make_command('switch', url), cwd=dest)

    def update(self, dest, url, rev_options):
        # type: (str, HiddenText, RevOptions) -> None
        cmd_args = make_command('pull', '-q', rev_options.to_args())
        self.run_command(cmd_args, cwd=dest)

    @classmethod
    def get_url_rev_and_auth(cls, url):
        # type: (str) -> Tuple[str, Optional[str], AuthInfo]
        # hotfix the URL scheme after removing bzr+ from bzr+ssh:// readd it
        url, rev, user_pass = super(Bazaar, cls).get_url_rev_and_auth(url)
        if url.startswith('ssh://'):
            url = 'bzr+' + url
        return url, rev, user_pass

    @classmethod
    def get_remote_url(cls, location):
        urls = cls.run_command(['info'], show_stdout=False, cwd=location)
        for line in urls.splitlines():
            line = line.strip()
            for x in ('checkout of branch: ',
                      'parent branch: '):
                if line.startswith(x):
                    repo = line.split(x)[1]
                    if cls._is_local_repository(repo):
                        return path_to_url(repo)
                    return repo
        return None

    @classmethod
    def get_revision(cls, location):
        revision = cls.run_command(
            ['revno'], show_stdout=False, cwd=location,
        )
        return revision.splitlines()[-1]

    @classmethod
    def is_commit_id_equal(cls, dest, name):
        """Always assume the versions don't match"""
        return False


vcs.register(Bazaar)
