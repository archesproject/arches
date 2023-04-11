from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = []
    initial = True

    operations = [
        migrations.CreateModel(
            name="Foo",
            fields=[
                ("foo", models.BooleanField()),
            ],
            options={"db_table": "foo", "managed": True,},
        ),
    ]