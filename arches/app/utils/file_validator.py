import io
import json
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
        match extension:
            case "DS_Store":
                if settings.FILE_TYPE_CHECKING == "lenient":
                    self.logger.log(
                        logging.WARN,
                        "DS_Store file encountered, proceeding with caution.",
                    )
                else:
                    errors.append(f"File type is not permitted: {extension}")
            case _ if (
                extension not in settings.FILE_TYPES
                and (settings.FILE_TYPE_CHECKING != "lenient" or extension is not None)
            ):
                errors.append(f"File type is not permitted: {extension}")
            case "xlsx":
                try:
                    load_workbook(io.BytesIO(file))
                except (InvalidFileException, zipfile.BadZipFile):
                    errors.append("Invalid xlsx workbook")
            case "csv":
                try:
                    datareader = csv.reader(
                        file.decode("utf-8").splitlines(), delimiter=","
                    )
                    length = None
                    for row in datareader:
                        if length is not None and length != len(row):
                            raise csv.Error("Invalid row length")
                        elif length is None:
                            length = len(row)
                except csv.Error:
                    errors.append("Invalid csv file")
            case "json":
                try:
                    json.load(io.BytesIO(file))
                except json.decoder.JSONDecodeError:
                    errors.append("Invalid json file")
            case _:
                if settings.FILE_TYPE_CHECKING != "lenient":
                    errors.append("Cannot validate file")

        for error in errors:
            self.logger.log(logging.ERROR, error)

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
                        if (
                            zip_file.filename.startswith("__MACOSX")
                            or zip_file.filename.lower().endswith("ds_store")
                            or zip_file.is_dir()
                        ):
                            continue
                        errors = errors + self.validate_file_type(
                            io.BytesIO(zip_ref.open(zip_file.filename).read()),
                            extension=zip_file.filename.split(".")[-1],
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
