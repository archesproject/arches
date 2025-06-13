from arches import VERSION as arches_version
from arches.app.datatypes import datatypes

from arches_querysets.datatypes import *


class DataTypeFactory(datatypes.DataTypeFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Until we're ready to upstream these changes, we have
        # to override some core Arches datatypes.
        self.overridden_datatype_instances = {
            "concept": ConceptDataType(),
            "concept-list": ConceptListDataType(),
            "file-list": FileListDataType(),
            "resource-instance": ResourceInstanceDataType(),
            "resource-instance-list": ResourceInstanceListDataType(),
            "string": StringDataType(),
            "url": URLDataType(),
        }

    def get_instance(self, datatype):
        try:
            instance = self.overridden_datatype_instances[datatype]
        except KeyError:
            instance = super().get_instance(datatype)

        if arches_version < (8, 0) and not hasattr(instance, "get_interchange_value"):
            instance.get_interchange_value = lambda value, **kwargs: value

        return instance
