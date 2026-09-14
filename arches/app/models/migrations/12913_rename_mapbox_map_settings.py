from django.db import migrations

SPRITES_NODE_ID = "0e900254-4148-11e7-9902-c4b301baab9f"
GLYPHS_NODE_ID = "0e90031e-4148-11e7-a176-c4b301baab9f"

OLD_SPRITES_DEFAULT = "mapbox://sprites/mapbox/basic-v9"
OLD_GLYPHS_DEFAULT = "mapbox://fonts/mapbox/{fontstack}/{range}.pbf"
NEW_SPRITES_DEFAULT = ""
NEW_GLYPHS_DEFAULT = "https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf"


def rename_node(Node, node_id, name, alias):
    Node.objects.filter(nodeid=node_id).update(name=name, alias=alias)


def update_tile_value(TileModel, node_id, old_value, new_value):
    for tile in TileModel.objects.filter(data__has_key=node_id):
        node_data = tile.data.get(node_id)
        if not isinstance(node_data, dict):
            continue
        changed = False
        for localized in node_data.values():
            if isinstance(localized, dict) and localized.get("value") == old_value:
                localized["value"] = new_value
                changed = True
        if changed:
            tile.save()


def forward(apps, schema_editor):
    Node = apps.get_model("models", "Node")
    TileModel = apps.get_model("models", "TileModel")

    rename_node(Node, SPRITES_NODE_ID, "MAPLIBRE_SPRITES", "maplibre_sprites")
    rename_node(Node, GLYPHS_NODE_ID, "MAPLIBRE_GLYPHS", "maplibre_glyphs")

    # Only rewrite values still set to the old Mapbox-hosted defaults; leave
    # any custom-configured sprite/glyph URLs untouched.
    update_tile_value(
        TileModel, SPRITES_NODE_ID, OLD_SPRITES_DEFAULT, NEW_SPRITES_DEFAULT
    )
    update_tile_value(TileModel, GLYPHS_NODE_ID, OLD_GLYPHS_DEFAULT, NEW_GLYPHS_DEFAULT)


def reverse(apps, schema_editor):
    Node = apps.get_model("models", "Node")
    TileModel = apps.get_model("models", "TileModel")

    rename_node(Node, SPRITES_NODE_ID, "MAPBOX_SPRITES", "mapbox_sprites")
    rename_node(Node, GLYPHS_NODE_ID, "MAPBOX_GLYPHS", "mapbox_glyphs")

    update_tile_value(
        TileModel, SPRITES_NODE_ID, NEW_SPRITES_DEFAULT, OLD_SPRITES_DEFAULT
    )
    update_tile_value(TileModel, GLYPHS_NODE_ID, NEW_GLYPHS_DEFAULT, OLD_GLYPHS_DEFAULT)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12779_add_multicard_resource_descriptor"),
    ]

    operations = [migrations.RunPython(forward, reverse)]
