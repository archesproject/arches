import uuid

from arches.app.datatypes import concept_types
from arches.app.utils.betterJSONSerializer import JSONSerializer


class ConceptDataType(concept_types.ConceptDataType):
    def transform_value_for_tile(self, value, **kwargs):
        if isinstance(value, uuid.UUID):
            return str(value)
        return self.transform_value_for_tile(value, **kwargs)

    def to_json(self, tile, node):
        data = self.get_tile_data(tile)
        if data:
            value_data = {}
            if val := data[str(node.nodeid)]:
                value_data = JSONSerializer().serializeToPython(
                    self.get_value(uuid.UUID(val))
                )
            return self.compile_json(tile, node, **value_data)

    def transform_value_for_tile(self, value, **kwargs):
        if isinstance(value, dict) and (value_id := value.get("valueid")):
            return self.transform_value_for_tile(value_id)
        return self.transform_value_for_tile(value)


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
        return self.transform_value_for_tile(joined_concept_id_strings, **kwargs)

    def to_json(self, tile, node):
        new_values = []
        data = self.get_tile_data(tile)
        if data:
            for val in data[str(node.nodeid)] or []:
                new_val = self.get_value(uuid.UUID(val))
                new_values.append(new_val)
        return self.compile_json(tile, node, concept_details=new_values)
