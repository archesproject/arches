#!/bin/bash

# Export all test data

source ../ENV/bin/activate

python manage.py packages -o export_graphs -d 'tests/fixtures/jsonld_base/models' -g ee72fb1e-fa6c-11e9-b369-3af9d3b32b71
mv tests/fixtures/jsonld_base/models/Test\ Complex\ Export.json tests/fixtures/jsonld_base/models/test_2_complex_object.json
python manage.py packages -o export_business_data -d 'tests/fixtures/jsonld_base/data' -f 'json' -g ee72fb1e-fa6c-11e9-b369-3af9d3b32b71
mv tests/fixtures/jsonld_base/data/Test_Complex_Export_* tests/fixtures/jsonld_base/data/test_2_instances.json
python manage.py packages -o export_business_data -d 'tests/fixtures/jsonld_base/data' -f 'json' -g c4d82c2c-fb5f-11e9-98e3-3af9d3b32b71
mv tests/fixtures/jsonld_base/data/5136_res_inst_plus_res_inst_* tests/fixtures/jsonld_base/data/test_3_instances.json

python manage.py packages -o export_graphs -d 'tests/fixtures/jsonld_base/models' -g 96867672-fbef-11e9-9ca4-3af9d3b32b71
mv tests/fixtures/jsonld_base/models/Nesting\ Test.json tests/fixtures/jsonld_base/models/nesting_test.json
python manage.py packages -o export_business_data -d 'tests/fixtures/jsonld_base/data' -f 'json' -g 96867672-fbef-11e9-9ca4-3af9d3b32b71
mv tests/fixtures/jsonld_base/data/Nesting_Test_* tests/fixtures/jsonld_base/data/test_nest_instances.json

curl http://localhost:8000/concepts/export/85995139-74c9-4133-8d42-c74f09d678c2 > tests/fixtures/jsonld_base/rdm/jsonld_test_thesaurus.xml
curl http://localhost:8000/concepts/export/collections > tests/fixtures/jsonld_base/rdm/jsonld_test_collections.xml

