rm cython.log > /dev/null 2> /dev/null
cd ../golismero
find `pwd` -name "*.py" > ../_tmp.txt
cd ../plugins
find `pwd` -name "*.py" >> ../_tmp.txt
cd ..
rm *.c > /dev/null 2> /dev/null
rm *.pyc > /dev/null 2> /dev/null
rm *.pyo > /dev/null 2> /dev/null

for f in $(cat _tmp.txt);
do
    cython $f >> tests/cython.log
done

rm _tmp.txt
find `pwd` -name "*.c" -delete > /dev/null 2> /dev/null
cd tests
