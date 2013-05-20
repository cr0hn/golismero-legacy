@echo off
cd ..\golismero
dir /b /s *.py > ..\_tmp.txt
cd ..\plugins
dir /b /s *.py >> ..\_tmp.txt
cd ..
for /F "tokens=*" %%A in (_tmp.txt) do C:\Python27\python.exe C:\Python27\Scripts\cython.py "%%A"
del _tmp.txt
del /s *.c > nul
cd tests
