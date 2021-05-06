# Casual Programming Language
Casual is a programming language designed to be as simple as possible, while being user-friendly.

# How to use the parser
I provide a setup.sh that installs the dependecies in a ubuntu-based system and a run.sh
that puts the parser to work.
Example of usage of run.sh:
  ```
  $ ./run.sh examples/valid1.cas
  ```

I also provide 5 syntatically valid and 4 syntatically invalid programs in the directory examples. Have in mind that you need to pass the
the directory along with the filename(as shown above) for the script to find the file.


## Language Description
Comments in Casual are started with the pound (#) character and finish at the end of the line.

* Casual is whitespace insensitive
* A program is made of several declarations or definitions
* A declaration includes the name of the function, its arguments and the returning type

 ```
 decl max (a:Int, b:Int):Int
 ```
 
* A definition has the same contents, but also has a block, corresponding to the body of the function:

``` 
def max (a:Int, b:Int):Int {
  if a > b {
    return a;
  }
  return b;
} 
``` 

* A block is always started and ended with curly parenthesis and features zero or more statements:
  * Return statements can have an expression or not (for Void functions): return; or return 1 + 1;
  * Expressions are statements: 1; or f(3);
  * if statements have (at least) a condition and a (then) block. Optionally they can have an else block, separated by a else keyword.
  * while blocks have a similar structure with a condition and a block.
  * Variable declarations require a type and a starting value a:Int = 0;
  * Variable assignments do not require the type a = 1.
* Expressions represent values. They can be:
  * Binary operators, with a C-like precedence and parenthesis to force other precedences: &&, ||, ==, !=, >=, >, <=, <, +, -, *, /, % em que a divisão tem sempre a semântica da divisão decimal.
  * The not unary operator (!true)
  * Boolean literals (true, false)
  * Integer literals (1, 01, 12312341341, 1_000_000) where underscores can be present in any position.
  * Float literals (1.1, .5, 1233123131231321)
  * String literals ("", "a", "aa", "qwertyuiop", "qwerty\tuiop")
  * Variables, which start with a letter or understore and are followed by any number of letters, underscores or numbers.
  * index access, (a[0] or get_array()[i+1])
  * function invocation (function(arg1, arg2)) where arguments can be expressions


Issues:
  - Currently it does not support arrays of array types
