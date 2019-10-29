#!/bin/bash

# Export all test data

source ../ENV/bin/activate

python manage.py packages -o export_graphs -d 'tests/fixtures/jsonld_base/models' -g ee72fb1e-fa6c-11e9-b369-3af9d3b32b71
mv tests/fixtures/jsonld_base/models/Test\ Complex\ Export.json tests/fixtures/jsonld_base/models/test_2_complex_object.json

python manage.py packages -o export_business_data -d 'tests/fixtures/jsonld_base/data' -f 'json' -g ee72fb1e-fa6c-11e9-b369-3af9d3b32b71


curl http://localhost:8000/concepts/export/ > thesaurus.xml
curl http://localhost:8000/concepts/export/collections > collections.xml


