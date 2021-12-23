import csv
import io
from importlib import import_module
import json
import logging
from django.db.models.functions import Lower
from arches.app.models.models import GraphModel, Node
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse

logger = logging.getLogger(__name__)

class ImportSingleCsv:
    def __init__(self, request=None):
        self.request = request

    def get_graphs(self, request):
        print("getting graphs")
        graphs = GraphModel.objects.all().exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        return graphs

    def get_nodes(self, request):
        print("getting nodes")
        graphid = request.POST.get('graphid')
        nodes = Node.objects.filter(graph_id=graphid).exclude(datatype__in=['semantic']).order_by(Lower('name'))
        # nodes = Node.objects.filter(graph_id=graphid).exclude(datatype__in=['semantic','concept','resource-instance', 'concept-list','resource-instance-list'])
        return nodes

    def read(self, request):
        """
        Reads added csv file and turn csv.reader or csv.DictReader object
        Reuiqres csv file and a flag indicating there is a header (can be handled in the front-end)
        Returns the reader object to display in a mapper && in a preview display
        """
        print("reading")
        file = request.FILES.get('file')
        csvfile = file.read().decode('utf-8')
        reader = csv.reader(io.StringIO(csvfile)) # returns iterator
        data = [line for line in reader]
        return data

    def validate(self, request):
        """
        Validate the csv file and return true / false
        User mapping is required
        Instantiate datatypes and validate the datatype?
        """
        print("validating")
        try:
            success = True
            message = "Everything looks good"
        except:
            success = False
            message = "There was an error"
        return JSONResponse({'success': False, 'message': message })

    def write(self, request):
        """
        Runs the actual import
        Returns done
        Must be a transaction
        Will sys.exit() work for stop in the middle of importing?
        """
        print("writing")        
        file = request.FILES.get('file')
        fieldnames = request.POST.get('fieldnames').split(',')
        csvfile = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(csvfile), fieldnames=fieldnames) # returns dictionary
        data = [line for line in reader]
        return data

