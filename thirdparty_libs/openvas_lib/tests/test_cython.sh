OLD_CWD=`pwd`
cd ..
find `pwd` -name "*.py" >> _tmp.txt

find . -name "*.c" -delete > /dev/null 2> /dev/null
find . -name "*.pyc" -delete > /dev/null 2> /dev/null
find . -name "*.pyo" -delete > /dev/null 2> /dev/null

for f in $(cat _tmp.txt);
do
    echo $f
    cython $f >> tests/cython.log
done

rm -rf _tmp.txt
find . -name "*.c" -delete > /dev/null 2> /dev/null
find . -name "*.pyc" -delete > /dev/null 2> /dev/null
find . -name "*.pyo" -delete > /dev/null 2> /dev/null

cd $OLD_CWD