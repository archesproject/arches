import csv
from arches.app.models.models import Concepts, Values
from arches.app.search.search_engine_factory import SearchEngineFactory

def LegacyIdsFixer(source):
    """
    Simple utility to replace unintelligible LegacyOIDs in uuid format with human readable ones.
    AZ 24/11/16
    """

    with open(source, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter= '|')
        for row in reader:
            try:
                concept = Concepts.objects.get(legacyoid = str(row['oldlegacy']))
            except:
                print "Concept %s could not be assigned value %s" % (row['oldlegacy'],row['newlegacy'])
            concept.legacyoid = row['newlegacy']
            concept.save()
            
def IndexConceptFixer(source):
    """
    Simple utility to delete the ES index of a given list of conceptids
    """

    with open(source, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter= '|')
        se = SearchEngineFactory().create() 
        for row in reader:
            try:
                
                conceptvalues = Values.objects.filter(conceptid = row['conceptid'])
                for conceptvalue in conceptvalues:
                    se.delete_terms(conceptvalue.valueid)
            except:
                print "Concept Value %s does not exist" % row['conceptid']
            