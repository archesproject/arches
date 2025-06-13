import uuid

from arches.app.datatypes import concept_types
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer


class ConceptDataType(concept_types.ConceptDataType):
    def transform_value_for_tile(self, value, **kwargs):
        if isinstance(value, dict) and (value_id := value.get("valueid")):
            return super().transform_value_for_tile(value_id)
        return super().transform_value_for_tile(value)

    def to_python(self, value, **kwargs):
        return self.get_instance(value)

    def to_json(self, tile, node):
        return {
            "@display_value": self.get_display_value(tile, node),
            "@details": self.get_details(tile, node),
        }

    def get_details(self, tile, node):
        data = self.get_tile_data(tile)
        value = data.get(str(node.nodeid))
        instance = self.get_instance(value)
        return JSONSerializer().serialize(instance)

    def get_instance(self, value):
        if value is None:
            return None
        try:
            value = uuid.UUID(value)
        except TypeError:
            pass
        return self.get_value(value)

    def get_interchange_value(self, value, *, details=None, **kwargs):
        if not value:
            return None
        if details is None:
            instance = self.get_instance(value)
            return JSONSerializer().handle_model(instance)
        return JSONDeserializer().deserialize(JSONSerializer().serialize(details))


class ConceptListDataType(concept_types.ConceptListDataType):
    def transform_value_for_tile(self, value, **kwargs):
        if not isinstance(value, list):
            value = [value]
        concept_id_strings = []
        for inner in value:
            if isinstance(inner, dict) and (
                concept_details := inner.get("concept_details")
            ):
                concept_id_strings.extend(
                    [detail["valueid"] for detail in concept_details]
                )
        joined_concept_id_strings = ",".join(concept_id_strings)
        return super().transform_value_for_tile(joined_concept_id_strings, **kwargs)

    def to_python(self, value, **kwargs):
        return self.get_instances(value) or None

    def to_json(self, tile, node):
        return {
            "@display_value": self.get_display_value(tile, node),
            "@details": self.get_details(tile, node),
        }

    def get_details(self, tile, node):
        data = self.get_tile_data(tile)
        value = data.get(str(node.nodeid))
        instances = self.get_instances(value)
        return [JSONSerializer().handle_model(inst) for inst in instances]

    def get_instances(self, value):
        new_values = []
        for inner_value in value or []:
            new_val = self.get_value(uuid.UUID(inner_value))
            new_values.append(new_val)
        return new_values

    def get_interchange_value(self, value, *, details=None, **kwargs):
        if not value:
            return None
        if details is None:
            details = [self.get_instances(value)]
        return JSONDeserializer().deserialize(JSONSerializer().serialize(details))
