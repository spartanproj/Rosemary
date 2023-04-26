# Rosemary
A blend of Python and C. Transpiled to C

For example, a basic program:
```c
float a=0
while a<1 {
    print "Enter number of scores: "
    input a
}
if a<=2 {
    print "a is 2"
}
float b=0
float s=0
print "Enter one value at a time: "
while b<a {
    input c
    float s=s+c
    float b=b+1
}

print "Average: "
print s/a
```

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
</table>

### Types: The list
#### Float
- Floating point decimal number
- Equivalent to C's `float`
#### Int
- Integer
- Equivalent to C's `int`
#### String
- String
- Equivalent to C's `char *`
- No segfaults (you hope)