import uuid
from itertools import chain

from arches.app.datatypes import concept_types
from arches.app.models.models import Value
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer


class ConceptDataType(concept_types.ConceptDataType):
    def transform_value_for_tile(self, value, **kwargs):
        if isinstance(value, dict) and (value_id := value.get("valueid")):
            return super().transform_value_for_tile(value_id)
        if isinstance(value, Value):
            return super().transform_value_for_tile(str(value.pk))
        return super().transform_value_for_tile(value)

    def to_python(self, value, **kwargs):
        return self.get_instance(value)

    def get_details(self, value, **kwargs):
        instance = self.get_instance(value)
        if not instance:
            return None
        return JSONDeserializer().deserialize(JSONSerializer().serialize([instance]))

    def get_instance(self, value):
        if value is None:
            return None
        try:
            value = uuid.UUID(value)
        except (TypeError, ValueError):
            pass
        return self.get_value(value)

    def get_display_value_context_in_bulk(self, values):
        value_ids = [
            value
            for value in values
            if value and uuid.UUID(value) not in self.value_lookup
        ]
        return Value.objects.filter(pk__in=value_ids)

    def set_display_value_context_in_bulk(self, datatype_context):
        for value in datatype_context:
            self.value_lookup[value.pk] = value


class ConceptListDataType(concept_types.ConceptListDataType):
    def transform_value_for_tile(self, value, **kwargs):
        if not value:
            return []
        if isinstance(value, list):
            if all(isinstance(val, Value) for val in value):
                return [str(val.pk) for val in value]
            return value
        return super().transform_value_for_tile(value, **kwargs)

    def to_python(self, value, **kwargs):
        return self.get_instances(value) or None

    def get_details(self, value, **kwargs):
        instances = self.get_instances(value)
        return JSONDeserializer().deserialize(JSONSerializer().serialize(instances))

    def get_instances(self, value):
        new_values = []
        for inner_value in value or []:
            try:
                new_val = self.get_value(uuid.UUID(inner_value))
            except (TypeError, ValueError):
                new_val = self.get_value(inner_value)
            new_values.append(new_val)
        return new_values

    def get_display_value(self, tile, node, **kwargs):
        new_values = []
        data = self.get_tile_data(tile)
        for val in data.get(str(node.nodeid)) or []:
            new_val = self.get_value(uuid.UUID(val))
            new_values.append(new_val.value)
        return ",".join(new_values)

    def get_display_value_context_in_bulk(self, values):
        not_null_values = [val for val in values if val]
        value_ids = list(chain(*not_null_values))
        return Value.objects.filter(pk__in=value_ids)

    def set_display_value_context_in_bulk(self, datatype_context):
        for value in datatype_context:
            self.value_lookup[value.pk] = value
