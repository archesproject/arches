#!/bin/bash

# Check to see if we are in our own dir or not
# Very brittle, should be improved
if [ ! -d "tests" ]; then
    cd ..
fi
source virtualenv/ENV/bin/activate

echo.
echo.
echo ----- RUNNING CORE ARCHES TESTS -----
echo.
python ../manage.py test tests --pattern="*.py"

deactivate
