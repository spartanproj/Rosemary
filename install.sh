git clone https://github.com/spartanproj/Rosemary ~/rsmy
cd ~/rsmy
function rsmy {
    python ~/rsmy/src/main.py $1 $1.c;
    gcc $1.c -o $1.o || clang $1.c -o $1.o
    printf "\n\nFilename is $(pwd)/$1.c"
}