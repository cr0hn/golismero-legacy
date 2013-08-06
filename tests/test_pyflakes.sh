rm pyflakes-out.log pyflakes-err.log > /dev/null 2> /dev/null
cd ../golismero
find `pwd` -name "*.py" > ../_tmp.txt
cd ../plugins
find `pwd` -name "*.py" >> ../_tmp.txt
cd ..
rm *.pyc > /dev/null 2> /dev/null
rm *.pyo > /dev/null 2> /dev/null

for f in $(cat _tmp.txt);
do
    pyflakes $f >> tests\pyflakes-out.log 2>> tests\pyflakes-err.log
done

rm _tmp.txt
cd tests