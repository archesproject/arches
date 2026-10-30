from django.db import migrations

MAPBOX_GEOCODER_ID = "10000000-0000-0000-0000-010000000000"


def restore_mapbox_geocoder(apps, schema_editor):
    Geocoder = apps.get_model("models", "Geocoder")
    Geocoder.objects.get_or_create(
        geocoderid=MAPBOX_GEOCODER_ID,
        defaults={
            "name": "Mapbox",
            "component": "views/components/geocoders/mapbox",
            "api_key": "",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("models", "12913_migrate_to_maplibre"),
    ]

    # The map uses MaplibreGeocoder directly; the geocoders registry is unused.
    operations = [
        migrations.RunPython(migrations.RunPython.noop, restore_mapbox_geocoder),
        migrations.DeleteModel(name="Geocoder"),
    ]
