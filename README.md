# Rosemary
## A blend of Python and C. Transpiled to C
## Why use Rosemary?
### Ease of use
- You can write short, efficient code
- Easy for both Python/Ruby or C/Java programmers to approach
### Speed
- It runs very fast (Takes <50 ms to compile to C)
- The program below, for example takes 13ms to compile.
For example, a basic program:
```c
ints a,b,c
while a<1 {
    print "Enter number of scores: "
    input a
}
if a<=2 {
    print "a is 2"
}
floats s
print "Enter one value at a time: "
while b<a {
    input c
    s+=c
    b++
}
print "Mean: "
print s/a
```
### Code insertion
- You can insert C directly into your program!
### Syntax
<table>
<tr>
<td> 

## Rosemary </td> <td> 
## C </td> <td> 
## Python </td>
</tr>
<tr>
<td> 

```c
if x>=1 {
    print "hi"
}
``` 

</td>
<td>

```c
if (x>=1) {
    printf("hi");
}
``` 

</td>
<td>

```py
if x>=1:
    print("hi")

``` 

</td>


<tr>
<td>

```c
float a = 0
while x>2 {
    input a
    print a
}
```

</td>
<td>

```c
float a = 0;
while (x>2) {
    scanf("%f",&a);
    printf("%d",a);
}
```

</td>
<td>

```py
while x>2:
    a=float(input())
    print(a)
```

</td>
</tr>
<tr>
<td>

```rust
loop 10 {
    print "hi"
}
```
</td>
<td>

```c
for (int x=0;x<10;x++) {
    printf("hi");
}
```

</td>
<td>

```py
for x in range(10):
    print("hi")
```

</td>
</tr>
<tr>
<td>

```c
int x=0
x+=1
print x
```
</td>
<td>

```c
int x=0;
x+=1;
print x;
```

</td>
<td>

```py
x=0;
x+=1;
print(x);
```

</td>
</tr>
<tr>
<td>

```c
int x=0
extern "x=3;"
print x
```
</td>
<td>

```c
int x=0;
x=3;
printf("%d",x)
```

</td>
<td>

```py
import cffi
print_banner("Building CFFI Module")
ffi = cffi.FFI()
this_dir = pathlib.Path().absolute()
h_file_name = this_dir / "c.h"
with open(h_file_name) as h_file:
    ffi.cdef(h_file.read())
ffi.set_source(
    "cffi_example",
    '#include "c.h"',
    libraries=["c"],
    library_dirs=[this_dir.as_posix()],
    extra_link_args=["-Wl,-rpath,."],
)
ffi.compile()
os.system("invoke build-cffi")
...
# It's not easy..
# This goes on and on and requires setup
```

</td>
</tr>
</table>

### Types: The list
#### Float
- Floating point decimal number
- Equivalent to C's `float`
#### Int
- Integer
- Equivalent to `<stdint.h>`'s `int64_t`
#### String
- String
- Equivalent to C's `char *`
- No segfaults (you hope)
