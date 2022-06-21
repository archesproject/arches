import io
import logging
import zipfile
from django.conf import settings
import filetype
import csv
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


class FileValidator(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def test_unknown_filetypes(self, file, extension=None):
        errors = []
        if extension in settings.FILE_TYPES:
            if extension == "xlsx":
                try:
                    load_workbook(io.BytesIO(file))
                except (InvalidFileException, zipfile.BadZipFile):
                    error = "Invalid xlsx workbook"
                    self.logger.log(logging.ERROR, error)
                    errors.append(error)
            elif extension == "csv":
                try:
                    datareader = csv.reader(file.decode("utf-8").splitlines(), delimiter=",")
                    length = None
                    for row in datareader:
                        if length is not None and length != len(row):
                            raise csv.Error("Invalid row length")
                        elif length is None:
                            length = len(row)
                except csv.Error:
                    error = "Invalid csv file"
                    self.logger.log(logging.ERROR, error)
                    errors.append(error)
            else:
                error = "Cannot validate file"
                self.logger.log(logging.ERROR, error)
                errors.append(error)
        else:
            error = "File type is not permitted"
            self.logger.log(logging.ERROR, error)
            errors.append(error)

        return errors

    def validate_file_type(self, file, extension=None):
        errors = []
        if settings.FILE_TYPE_CHECKING:
            contents = file.read()
            file_type = filetype.guess(contents)
            if file_type is None or extension == "xlsx":
                errors = errors + self.test_unknown_filetypes(contents, extension)
                return errors

            if file_type.extension == "zip":
                with zipfile.ZipFile(file, "r") as zip_ref:
                    files = zip_ref.infolist()
                    for zip_file in files:
                        if not zip_file.filename.startswith("__MACOSX") and not zip_file.is_dir():
                            errors = errors + self.validate_file_type(
                                io.BytesIO(zip_ref.open(zip_file.filename).read()), extension=zip_file.filename.split(".")[-1]
                            )
                    if len(errors) > 0:
                        error = "Unsafe zip file contents"
                        errors.append(error)
                        self.logger.log(logging.ERROR, error)

            if file_type.extension not in settings.FILE_TYPES:
                error = "Unsafe file type {}".format(str(file_type.extension))
                errors.append(error)
                self.logger.log(logging.ERROR, error)

            file.seek(0)

        return errors
