from arches.app.datatypes.base import BaseDataType
from arches.app.models import models
from arches.app.models.system_settings import settings

sample_widget = models.Widget.objects.get(name="sample-widget")

details = {
    "datatype": "sample-datatype",
    "iconclass": "fa fa-file-code-o",
    "modulename": "datatypes.py",
    "classname": "SampleDataType",
    "defaultwidget": sample_widget,
    "defaultconfig": None,
    "configcomponent": None,
    "configname": None,
    "isgeometric": False,
    "issearchable": True,
}


class SampleDataType(BaseDataType):
    def validate(self, value, row_number=None, source=None, node=None, nodeid=None, strict=False):
        errors = []
        try:
            value.upper()
        except Exception:
            errors.append(
                {
                    "type": "ERROR",
                    "message": "datatype: {0} value: {1} {2} {3} - {4}. {5}".format(
                        self.datatype_model.datatype, value, row_number, source, "this is not a string", "This data was not imported."
                    ),
                }
            )
        return errors

    def append_to_document(self, document, nodevalue, nodeid, tile):
        document["strings"].append({"string": nodevalue, "nodegroup_id": tile.nodegroup_id})

    def transform_export_values(self, value, *args, **kwargs):
        if value is not None:
            return value.encode("utf8")

    def get_search_terms(self, nodevalue, nodeid=None):
        terms = []
        if nodevalue is not None:
            if settings.WORDS_PER_SEARCH_TERM is None or (len(nodevalue.split(" ")) < settings.WORDS_PER_SEARCH_TERM):
                terms.append(nodevalue)
        return terms

    def append_search_filters(self, value, node, query, request):
        try:
            if value["val"] != "":
                match_type = "phrase_prefix" if "~" in value["op"] else "phrase"
                match_query = Match(field="tiles.data.%s" % (str(node.pk)), query=value["val"], type=match_type)
                if "!" in value["op"]:
                    query.must_not(match_query)
                    query.filter(Exists(field="tiles.data.%s" % (str(node.pk))))
                else:
                    query.must(match_query)
        except KeyError as e:
            pass
