@echo off
del pyflakes.log > nul 2> nul
cd ..\golismero
dir /b /s *.py > ..\_tmp.txt
cd ..\plugins
dir /b /s *.py >> ..\_tmp.txt
cd ..
del /s *.pyc > nul 2> nul
del /s *.pyo > nul 2> nul
for /F "tokens=*" %%A in (_tmp.txt) do C:\Python27\python.exe C:\Python27\Scripts\pyflakes-script.py "%%A" >> tests\pyflakes.log
del _tmp.txt
cd tests
