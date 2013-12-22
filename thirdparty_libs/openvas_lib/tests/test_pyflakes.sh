rm pyflakes-out.log pyflakes-err.log > /dev/null 2> /dev/null

OLD_PWD=`pwd`

cd ..
find `pwd` -name "*.py" > _tmp.txt
find . -name "*.pyc" -delete > /dev/null 2> /dev/null
find . -name "*.pyo" -delete > /dev/null 2> /dev/null

for f in $(cat _tmp.txt);
do
    pyflakes $f >> tests/pyflakes-out.log 2>> tests/pyflakes-err.log
done

rm _tmp.txt
find . -name "*.pyc" -delete > /dev/null 2> /dev/null
find . -name "*.pyo" -delete > /dev/null 2> /dev/null

cd $OLD_PWD
