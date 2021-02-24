import uuid
import csv
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from arches.app.models import models
from arches.app.models import concept
from arches.app.models.system_settings import settings
from arches.app.datatypes.base import BaseDataType
from arches.app.datatypes.datatypes import DataTypeFactory, get_value_from_jsonld
from arches.app.models.concept import get_preflabel_from_valueid, get_preflabel_from_conceptid, get_valueids_from_concept_label
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Range, Term, Nested, Exists, Terms
from arches.app.utils.date_utils import ExtendedDateFormat
# for the RDF graph export helper functions
from rdflib import Namespace, URIRef, Literal, BNode
from rdflib import ConjunctiveGraph as Graph
from rdflib.namespace import RDF, RDFS, XSD, DC, DCTERMS, SKOS
from arches.app.models.concept import ConceptValue

archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
cidoc_nm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


class BaseConceptDataType(BaseDataType):
    def __init__(self, model=None):
        super(BaseConceptDataType, self).__init__(model=model)
        self.value_lookup = {}

    def get_value(self, valueid):
        try:
            return self.value_lookup[valueid]
        except:
            try:
                self.value_lookup[valueid] = models.Value.objects.get(pk=valueid)
                return self.value_lookup[valueid]
            except ObjectDoesNotExist:
                return models.Value()

    def get_concept_export_value(self, valueid, concept_export_value_type=None):
        ret = ""
        if valueid is None or valueid.strip() == "":
            pass
        elif concept_export_value_type is None or concept_export_value_type == "" or concept_export_value_type == "label":
            ret = self.get_value(valueid).value
        elif concept_export_value_type == "both":
            ret = valueid + "|" + self.get_value(valueid).value
        elif concept_export_value_type == "id":
            ret = valueid
        return ret

    def get_concept_dates(self, concept):
        result = None
        date_range = {}
        values = models.Value.objects.filter(concept=concept)
        for value in values:
            if value.valuetype.valuetype in ("min_year" "max_year"):
                date_range[value.valuetype.valuetype] = value.value
        if "min_year" in date_range and "max_year" in date_range:
            result = date_range
        return result

    def append_to_document(self, document, nodevalue, nodeid, tile, provisional=False):
        try:
            assert isinstance(nodevalue, (list, tuple))  # assert nodevalue is an array
        except AssertionError:
            nodevalue = [nodevalue]
        for valueid in nodevalue:
            value = self.get_value(valueid)
            date_range = self.get_concept_dates(value.concept)
            if date_range is not None:
                min_date = ExtendedDateFormat(date_range["min_year"]).lower
                max_date = ExtendedDateFormat(date_range["max_year"]).upper
                if {"gte": min_date, "lte": max_date} not in document["date_ranges"]:
                    document["date_ranges"].append(
                        {"date_range": {"gte": min_date, "lte": max_date}, "nodegroup_id": tile.nodegroup_id, "provisional": provisional}
                    )
            document["domains"].append(
                {
                    "label": value.value,
                    "conceptid": value.concept_id,
                    "valueid": valueid,
                    "nodegroup_id": tile.nodegroup_id,
                    "provisional": provisional,
                }
            )
            document["strings"].append({"string": value.value, "nodegroup_id": tile.nodegroup_id, "provisional": provisional})

    def append_search_filters(self, value, node, query, request):
        try:
            if value["op"] == "null" or value["op"] == "not_null":
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                match_query = Match(field="tiles.data.%s" % (str(node.pk)), type="phrase", query=value["val"])
                if "!" in value["op"]:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)

        except KeyError as e:
            pass


class ConceptDataType(BaseConceptDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []
        # first check to see if the validator has been passed a valid UUID,
        # which should be the case at this point. return error if not.
        if value is not None:
            if type(value) == list:
                message = _("The widget used to save this data appears to be incorrect for this datatype. Contact system admin to resolve")
                error_message = self.create_error_message(value, source, row_number, message)
                errors.append(error_message)
                return errors

            try:
                uuid.UUID(str(value))
            except ValueError:
                message = _("This is an invalid concept prefLabel, or an incomplete UUID")
                error_message = self.create_error_message(value, source, row_number, message)
                errors.append(error_message)
                return errors

            try:
                models.Value.objects.get(pk=value)
            except ObjectDoesNotExist:
                message = _("This UUID is not an available concept value")
                error_message = self.create_error_message(value, source, row_number, message)
                errors.append(error_message)
                return errors
        return errors

    def transform_value_for_tile(self, value):
        return value.strip()

    def transform_export_values(self, value, *args, **kwargs):
        concept_export_value_type = kwargs.get("concept_export_value_type", None)
        return self.get_concept_export_value(value, concept_export_value_type)

    def get_pref_label(self, nodevalue, lang="en-US"):
        return get_preflabel_from_valueid(nodevalue, lang)["value"]

    def get_display_value(self, tile, node):
        data = self.get_tile_data(tile)
        if data[str(node.nodeid)] is None or data[str(node.nodeid)].strip() == "":
            return ""
        else:
            return self.get_value(uuid.UUID(data[str(node.nodeid)])).value

    def get_rdf_uri(self, node, data, which="r"):
        if not data:
            return None
        c = ConceptValue(str(data))
        assert c.value is not None, "Null or blank concept value"
        ext_ids = [
            ident.value for ident in models.Value.objects.all().filter(concept_id__exact=c.conceptid, valuetype__category="identifiers")
        ]
        for p in settings.PREFERRED_CONCEPT_SCHEMES:
            for id_uri in ext_ids:
                if str(id_uri).startswith(p):
                    return URIRef(id_uri)
        return URIRef(archesproject[f"concepts/{c.conceptid}"])

    def to_rdf(self, edge_info, edge):
        g = Graph()
        myuri = self.get_rdf_uri(None, edge_info["range_tile_data"])
        if edge_info["r_uri"] == myuri:
            c = ConceptValue(str(edge_info["range_tile_data"]))
            g.add((edge_info["r_uri"], RDF.type, URIRef(edge.rangenode.ontologyclass)))
            g.add((edge_info["d_uri"], URIRef(edge.ontologyproperty), edge_info["r_uri"]))
            g.add((edge_info["r_uri"], URIRef(RDFS.label), Literal(c.value)))
        return g

    def from_rdf(self, json_ld_node):
        # Expects a label and a concept URI within the json_ld_node, might not always get them both

        try:
            # assume a list, and as this is a ConceptDataType, assume a single entry
            json_ld_node = json_ld_node[0]
        except KeyError as e:
            pass

        concept_uri = json_ld_node.get("@id")
        label_node = json_ld_node.get(str(RDFS.label))
        concept_id = lang = None
        import re

        # FIXME: This should use settings for host and check for UUID
        p = re.compile(r"(http|https)://(?P<host>[^/]*)/concepts/(?P<concept_id>[A-Fa-f0-9\-]*)/?$")
        m = p.match(concept_uri)
        if m is not None:
            concept_id = m.groupdict().get("concept_id")
        else:
            # could be an external id, rather than an Arches only URI
            hits = [ident for ident in models.Value.objects.all().filter(value__exact=str(concept_uri), valuetype__category="identifiers")]
            if len(hits) == 1:
                concept_id = hits[0].concept_id
            else:
                print("ERROR: Multiple hits for {0} external identifier in RDM:".format(concept_uri))
                for hit in hits:
                    print("ConceptValue {0}, Concept {1} - '{2}'".format(hit.valueid, hit.conceptid, hit.value))
                # Just try the first one and hope
                concept_id = hits[0].concept_id

        if label_node:
            label, lang = get_value_from_jsonld(label_node)
            if label:
                values = get_valueids_from_concept_label(label, concept_id, lang)
                if values:
                    return values[0]["id"]
                else:
                    if concept_id:
                        hits = [ident for ident in models.Value.objects.all().filter(value__exact=label)]
                        if hits and len(hits) == 1:
                            return str(hits[0].pk)
                        label = None
                    else:
                        print("No Concept ID URI supplied for rdf")
        else:
            label = None

        if concept_id and label is None:
            value = get_preflabel_from_conceptid(concept_id, lang=lang)
            if value["id"]:
                return value["id"]
            else:
                hits = [ident for ident in models.Value.objects.all()]
                if hits:
                    return str(hits[0].pk)
                else:
                    print(f"No labels for concept: {concept_id}!")
                    return None
        else:
            # No concept_id means not in RDM at all
            return None


    def ignore_keys(self):
        return ["http://www.w3.org/2000/01/rdf-schema#label http://www.w3.org/2000/01/rdf-schema#Literal"]


class ConceptListDataType(BaseConceptDataType):
    def validate(self, value, row_number=None, source="", node=None, nodeid=None):
        errors = []

        # iterate list of values and use the concept validation on each one
        if value is not None:
            validate_concept = DataTypeFactory().get_instance("concept")
            for v in value:
                val = v.strip()
                errors += validate_concept.validate(val, row_number)
        return errors

    def transform_value_for_tile(self, value):
        ret = []
        for val in csv.reader([value], delimiter=",", quotechar='"'):
            for v in val:
                ret.append(v.strip())
        return ret

    def transform_export_values(self, value, *args, **kwargs):
        new_values = []
        for val in value:
            new_val = self.get_concept_export_value(val, kwargs.get("concept_export_value_type", None))
            new_values.append(new_val)
        return ",".join(new_values)

    def get_display_value(self, tile, node):
        new_values = []
        data = self.get_tile_data(tile)
        if data[str(node.nodeid)]:
            for val in data[str(node.nodeid)]:
                new_val = self.get_value(uuid.UUID(val))
                new_values.append(new_val.value)
        return ",".join(new_values)

    def get_rdf_uri(self, node, data, which="r"):
        c = ConceptDataType()
        if not data:
            print(f"concept-list got data without values: {node}, {data}")
            return []
        return [c.get_rdf_uri(node, d, which) for d in data]

    def to_rdf(self, edge_info, edge):
        g = Graph()
        c = ConceptDataType()
        if edge_info["range_tile_data"]:
            for r in edge_info["range_tile_data"]:
                concept_info = edge_info.copy()
                concept_info["range_tile_data"] = r
                g += c.to_rdf(concept_info, edge)
        return g

    def from_rdf(self, json_ld_node):
        # returns a list of concept ids
        ctype = ConceptDataType()
        if isinstance(json_ld_node, list):
            return [ctype.from_rdf(item) for item in json_ld_node]
        else:
            return [ctype.from_rdf(json_ld_node)]

    def collects_multiple_values(self):
        return True

    def ignore_keys(self):
        return ["http://www.w3.org/2000/01/rdf-schema#label http://www.w3.org/2000/01/rdf-schema#Literal"]