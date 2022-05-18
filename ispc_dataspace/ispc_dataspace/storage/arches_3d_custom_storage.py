import os

from storages.backends.azure_storage import AzureStorage
from django.contrib.staticfiles.storage import HashedFilesMixin, ManifestFilesMixin, ManifestStaticFilesStorage, StaticFilesStorage
from django.utils.six.moves.urllib.parse import unquote, urlsplit, urlunsplit

from .extract_mixin import ExtractMixin

import logging

logger = logging.getLogger(__name__)


class Arches3dCustomStorage(ExtractMixin, AzureStorage):
    pass

class Arches3DCustomStorageHashedFilesMixin(HashedFilesMixin):
    def hashed_name(self, name, content=None, filename=None):
        # `filename` is the name of file to hash if `content` isn't given.
        # `name` is the base name to construct the new hashed filename from.
        parsed_name = urlsplit(unquote(name))
        clean_name = parsed_name.path.strip()
        if filename:
            filename = urlsplit(unquote(filename)).path.strip()
        filename = filename or clean_name
        opened = False
        if content is None:
            if not self.exists(filename):
                logging.warning("The file '%s' could not be found with %r. Continuing..." % (filename, self))
                return name
            try:
                content = self.open(filename)
            except IOError:
                # Handle directory paths and fragments
                return name
            opened = True
        try:
            file_hash = self.file_hash(clean_name, content)
        finally:
            if opened:
                content.close()
        path, filename = os.path.split(clean_name)
        root, ext = os.path.splitext(filename)
        if file_hash is not None:
            file_hash = ".%s" % file_hash
        hashed_name = os.path.join(path, "%s%s%s" %
                                   (root, file_hash, ext))
        unparsed_name = list(parsed_name)
        unparsed_name[2] = hashed_name
        # Special casing for a @font-face hack, like url(myfont.eot?#iefix")
        # http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax
        if '?#' in name and not unparsed_name[3]:
            unparsed_name[2] += '?'
        return urlunsplit(unparsed_name)

class Arches3dCustomStorageManifestFilesMixin(Arches3DCustomStorageHashedFilesMixin, ManifestFilesMixin):
    pass

class Arches3dCustomStorageManifestStaticFilesStorage(Arches3dCustomStorageManifestFilesMixin, ManifestStaticFilesStorage):
    pass

class Arches3dCustomStorageStatic(StaticFilesStorage, AzureStorage):
    def _save(self, name, content):
        Arches3dCustomStorageManifestStaticFilesStorage()._save(name, content)
        AzureStorage()._save(name, content)
        return name
