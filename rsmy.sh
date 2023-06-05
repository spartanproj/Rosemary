location=$(dirname $( realpath $0))
python $location/src/main.py $1 $1.c -std -file -math
gcc $1.c -o $1.o -Wno-unused-function -Wno-unused-variable -Wno-return-type
./$1.o