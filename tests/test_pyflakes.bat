@echo off
del pyflakes-out.log > nul 2> nul
del pyflakes-err.log > nul 2> nul
cd ..\golismero
dir /b /s *.py > ..\_tmp.txt
cd ..\plugins
dir /b /s *.py >> ..\_tmp.txt
cd ..
del /s *.pyc > nul 2> nul
del /s *.pyo > nul 2> nul
if exist C:\Python27\Scripts\flake8-script.py goto use_flake8
if exist C:\Python27\Scripts\pyflakes-script.py goto use_pyflakes
if exist C:\Python27\Scripts\pep8-script.py goto use_pep8
echo Neither PyFlakes, PEP8 nor Flake8 were found!
goto end

:use_flake8
for /F "tokens=*" %%A in (_tmp.txt) do C:\Python27\python.exe C:\Python27\Scripts\flake8-script.py "%%A" >> tests\flake8-out.log 2>> tests\flake8-err.log
goto end

:use_pyflakes
for /F "tokens=*" %%A in (_tmp.txt) do C:\Python27\python.exe C:\Python27\Scripts\pyflakes-script.py "%%A" >> tests\pyflakes-out.log 2>> tests\pyflakes-err.log
if exist C:\Python27\Scripts\pep8-script.py goto use_pep8
goto end

:use_pep8
for /F "tokens=*" %%A in (_tmp.txt) do C:\Python27\python.exe C:\Python27\Scripts\pep8-script.py "%%A" >> tests\pep8-out.log 2>> tests\pep8-err.log
goto end

:end
del _tmp.txt
cd tests
