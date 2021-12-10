import csv
import io
from importlib import import_module
import logging

logger = logging.getLogger(__name__)

class ImportSingleCsv:
    def __init__(self, request=None):
        self.request = request

    def add(self, request):
        """
        Reads added csv file and turn csv.reader or csv.DictReader object
        Reuiqres csv file and a flag indicating there is a header (can be handled in the front-end)
        Returns the reader object to display in a mapper && in a preview display
        """
        file = request.FILES.get('file')
        csvfile = file.read().decode('utf-8')
        reader = csv.reader(io.StringIO(csvfile))
        data = [line for line in reader]
        print(data)
        return data

    def validate(self, request):
        """
        Validate the csv file and return true / false
        User mapping is required
        Instantiate datatypes and validate the datatype?
        """
        return True

    def run(self, request):
        """
        Runs the actual import
        Returns done
        Must be a transaction
        sys.exit() will work for stop in the middle of importing
        """
        return "run"
