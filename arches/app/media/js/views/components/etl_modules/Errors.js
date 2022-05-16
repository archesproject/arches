General issues
1. %20-%20 in the file name : branch-csv-importer.js L.68
2. my EXCEL does not like xls -> xlsx: branch-csv-importer.js L.68
3. it does not delete the files, I guess, if task fails
4. nice to have an error message, something other validation error happens

concept / concept-list datatype
1. uuid or value both working
2. concept-list only works with csv w/o spaces
3. does NOT check whether in the right concept collection

number (Core issue)
1. number datatype needs to catch ValueError: datatypes.py L.186
"six"x; "6"o

boolean
1. true: y, yes, t, true, on and 1;
   false: n, no, f, false, off and 0 (based on distutils.util.strtobool)

date / datetime (Core issue)
1. the value from excel is already a datetime (not always) so fails datatypes.py L.361-365
2. force it to be string '2022-03-04

resource / resource-list
1. add more than one if passed for resource datetype (not list)
2. accept only list of the object form
[{"resourceid": "00f3c4cf-2034-420c-855d-05e8cb45436e", "ontologyProperty": "", "inverseOntologyProperty": "", "resourceXresourceid": ""}]
- 3. if resourceid isn't avalable, what happens?
- 4. resourceidxResourceId? double check?
    create resource x resource record and then add to the tile?


domain / domain-list
1. bug? domains changes other nodes domains changes (inconsistently)
2. not working with value just uuid
3. if domain id is not available, no error but no value in the node either
4. csv domain is working for domain-list, fails for domain (as expected)

edtf
- 1. Causing a problem because the transform_value_for_tile return a tuple

url
1. accepts both {"url": "https://google.com", "url_label": "Google" } or just https://google.com
