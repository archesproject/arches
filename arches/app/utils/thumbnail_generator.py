"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
from tempfile import NamedTemporaryFile

from django.utils.translation import gettext as _


class ThumbnailGenerator(object):

    def make_thumbnail(self, inputfile_path, outputfile_path, **kwargs):
        """
        Args:
            inputfile_path: a path to a file on disk to create a thumbnail from
            outputfile_path: a path to a file on disk where the thumbnail will be written to

        Returns:
            None
        """

        raise NotImplementedError  # subclasses should implement this method

    def get_thumbnail_data(self, uploadedfile):
        """
        Args:
            uploadedfile: a Django File object

        Returns:
            binary representation of that file as a thumbnail
        """

        binary_data = None

        with NamedTemporaryFile(suffix=".png") as thumbnail:
            try:
                # uploaded files that are large enough get written to a TemporaryUploadedFile
                # and have a temporary_file_path
                self.make_thumbnail(uploadedfile.temporary_file_path(), thumbnail.name)
            except AttributeError as e:
                # small files are uploaded to an InMemoryUploadedFile
                # and don't have a temporary_file_path hence the except clause
                # because there's not file written to disk when initially uploaded, we need to make one
                uploadedfile_extension = f".{uploadedfile.name.split('.')[-1]}"
                with NamedTemporaryFile(suffix=uploadedfile_extension) as tempfile:
                    for chunk in uploadedfile.chunks():
                        tempfile.write(chunk)
                    tempfile.seek(0)
                    self.make_thumbnail(tempfile.name, thumbnail.name)

            # for some reason thumbnails of video files can still end up being very large
            # this tries to take care of that by making a thumbnail of the "large" thumbnail
            if os.stat(thumbnail.name).st_size > 500000:
                with NamedTemporaryFile(suffix=".png") as tempfile:
                    self.make_thumbnail(thumbnail.name, tempfile.name)
                    binary_data = tempfile.read()
            else:
                binary_data = thumbnail.read()

        return binary_data


class ThumbnailGenerationError(Exception):
    def __init__(
        self,
        message=_("Unable to generate a thumbnail from the supplied file."),
        code=None,
    ):
        self.title = _("Thumbnail Generation Error")
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)
