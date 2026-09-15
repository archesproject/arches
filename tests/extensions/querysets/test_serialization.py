from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.extensions.querysets.utils.tests import GraphTestCase


class SerializationTests(GraphTestCase):
    def test_serialization_via_better_json_serializer(self):
        dict_string = JSONSerializer().serialize(self.resource_42)
        resource_dict = JSONDeserializer().deserialize(dict_string)
        # Django model fields are present.
        self.assertIn("graph_id", resource_dict)
        tile_dict = resource_dict["aliased_data"]["datatypes_1"]
        self.assertIn("nodegroup_id", tile_dict)
        # Node values are present.
        self.assertIn("non_localized_string_alias", tile_dict["aliased_data"])
        # Special properties are not present.
        self.assertNotIn("data", tile_dict)
        self.assertNotIn("parent", tile_dict)

        # Child tiles appear under nodegroup aliases.
        child_tile_dict = tile_dict["aliased_data"]["datatypes_1_child"]
        self.assertIn("tileid", child_tile_dict)

        # Cardinality N tiles appear in an array.
        tile_list = resource_dict["aliased_data"]["datatypes_n"][0]
        child_tile_list = tile_list["aliased_data"]["datatypes_n_child"]
        self.assertIn("tileid", child_tile_list[0])
