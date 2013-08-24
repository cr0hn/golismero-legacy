@echo off
set script="%~dp0\golismero.py"
shift
python %script% %*
