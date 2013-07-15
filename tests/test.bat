@echo off
call test_cython.bat
call test_pyflakes.bat
python test_pylint.py
python test_pychecker.py > test-out.log 2> test-err.log
python test_data.py >> test-out.log 2>> test-err.log
python test_url.py >> test-out.log 2>> test-err.log
python test_http_parser.py >> test-out.log 2>> test-err.log
python test_auditdb.py >> test-out.log 2>> test-err.log
python test_cachedb.py >> test-out.log 2>> test-err.log
python test_parallel.py >> test-out.log 2>> test-err.log
