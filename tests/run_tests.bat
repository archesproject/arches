cd %~dp0..
call "virtualenv/ENV/Scripts/activate.bat"
echo.
echo.
echo ----- RUNNING CORE ARCHES TESTS -----
echo.

python manage.py test tests --pattern="*.py"

call "virtualenv/ENV/Scripts/deactivate.bat"
pause