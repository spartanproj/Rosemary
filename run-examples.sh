function rsmy {
    python ~/coding/rsmy/src/main.py $1 $1.c;
    gcc $1.c -o $1.o
    printf "\n\nFilename is $(pwd)/$1.o\n\n"
    printf "$1.o - source $1\n\n"
    ./$1.o
}

printf "Calcuating the Fibonacci sequence\n"
rsmy examples/fib.rsmy
sleep 5
printf "Mean of values\n"
rsmy examples/mean.rsmy
sleep 5
printf "Range of values\n"
rsmy examples/range.rsmy
sleep 5
printf "String manipulation\n"
rsmy examples/string.rsmy
sleep 5
printf "Using external C code\n"
rsmy examples/extern.rsmy
rm -rf examples/*.rsmy.c
rm -rf examples/*.rsmy.o