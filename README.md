# OWScript
Python-like scripting language which transpiles into Overwatch Workshop script rulesets.

Setup
=====
## Installation & Usage
1. Install Python with `pip` if you have not done so already.
2. Run the command `python OWScript.py` with the following arguments:
- `input` Path to input file, blank for stdin
- `-m | --min` Optional: minifies the output by stripping whitespace
- `-s | --save [FILE]` Optional: saves to the target output file instead of stdout
- `-c | --copy` Optional: copies code to clipboard (must have *pyperclip* installed: `pip install pyperclip`)

**NPM Integration** by @MatthewSH
[OWScript NPM Package](https://www.npmjs.com/package/owscript)

## Syntax Highlighting

**Visual Studio Code**
Download the latest [OWScript extension](https://marketplace.visualstudio.com/items?itemName=adapap.owscript) from the marketplace.

**Sublime Text 3**
In the `Syntax/` folder, you can find the raw Iro code which I used to generate a Sublime Text file with modifications. You can directly import the `OWScript.sublime-syntax` file by putting it in your ST3 `User` folder.

Projects
========
- **Cookie Clicker** [![Discord Shield](https://discordapp.com/api/guilds/572937743114436619/widget.png?style=shield "Made by @adapap")](https://discord.gg/5Nst8g5)
- [**Upgrade Shop**](https://github.com/overwatchworkshop/upgrade-shop)

Documentation
=============
*See example code in the `Examples/` folder.*

**Input** `*.owpy`

**Output** `*.ows` (standard as agreed upon voting results)

**Semantic**
* [Values / Actions](#values--actions)
* [Annotations / Comments](#annotations--comments)
* [Assignment / Arithmetic](#assignment--arithmetic)
* [Logic](#logic)
* [Functions](#functions)
* [Loops](#loops)
* [Attributes / Methods](#attributes--methods)
* [Imports](#imports)

**Data Types & Structures**
* [Variables](#variables)
* [Strings](#strings)
* [Vectors](#vectors)
* [Time](#time)
* [Arrays](#arrays)
* [Alias Table](#alias-table)

## Notes
- Be sure not to conflict variable/function names with built-in functions such as `Add`, `Wait`, or `Damage`.
- Many commonly used values have been aliased in order to reduce verbosity. See the table at the bottom for the list of built-in aliases.
- If you have an unexpected error/suggestion, feel free to submit an issue
  - Alternatively, I am open to pull requests if you want to contribute

## Values / Actions
Values and actions are the main types that come up when working in the Workshop. In general, anything with parameters can be written in two ways (which can be interchanged):

**Indented Blocks**
```
Round
    Count Of
        All Players
            Team 2
    Up
```
**Parenthesized / Literal**
```
Round(Count Of(All Players(Team 2)), Up) /* Same as output */
```

## Annotations / Comments
Annotations are ways to remind yourself what the type of a variable. It is written as text followed by a colon. Comments are written as most traditional languages (`// line comment`, `/* multiline comment */`). Both are ignored in the code output.
```
Event
    /* Set up event attributes */
    Event_Type: Ongoing - Event Player // Event_Type is an annotation (cannot have spaces!)
    Annotation_2: All
```

## Assignment / Arithmetic
Assignment (regular and augmented), as well as most arithmetic operators work as they do in Python or other traditional programming languages. Operators include: `+ - * / ^ %` as well as the augmented equivalents: `+= -= *= /= ^= %=`
```
a = 1
a += -1
a *= 3
a = a ^ (a + a) % 3
```

## Logic
Boolean logic is implemented exactly as in Python. The operators `and`, `or`, and `not` function as C-style `&&`, `|
|`, and `!`. Comparison operators include the traditional `<`, `>`, `<=`, `>=`, `!=`, `==` as well as containment operators `in` and `not in`.
```
b = True and not True
Count Of
    Everyone
== 12 // The reason why == 12 is here is to distinguish between the constant "Everyone" and the value "Count Of".
// You can choose to write this expression inline for less ambiguity:
Count Of(Everyone) == 12
y = Event Player in Players In Radius(<1, 2, 3>, 15)
```

## Variables
Variables are ways to reference values using a name. Their type is stored when they are defined.

**Global Variables (default)**
```
gvar hero_index = 1
global_time = 60s // default type is global
```
**Player Variables**
```
pvar score = 2 // pvar is only needed when defining a variable
pvar score@Event Player = 3 // Event Player (default) is the player which the variable will be bound to
score += 1 // modifies the pvar score
```
**Const**
```
const cost = 100
/* const cannot be modified and directly outputs the value,
rather than outputting Value In Array(...) */
```

Using the technique from [@ItsDeltin](https://github.com/ItsDeltin), the limit to
the number of variables that can be created is the maximum length of an array (\~1000 variables).

## Strings
String literals are enclosed with quotes. Formatted strings are made with enclosing backticks, using `{}` whenever you want to use a variable instead of a string constant.
```
Rule "String Demo"
    Event
        On Each Player
        All
        All
    Actions
        Msg(Event Player, "Hello") // Alias for Small Message
        Big Msg(Event Player, `Money: {}`(pvar money)) // Example formatted string
        Small Msg(Event Player, `Unlocked {} / {}: Victory!`(5, 5)) // More advanced formatted string
```

## Vectors
Vectors can be created in 3 ways as well:

**Literal**
```
Vector(1, 2, 3)
```
**Block**
```
Vector
    1
    2
    3
```
**Idiomatic**
```
<1, 2, 3>
```

## Time
Time can be represented in *ms*, *s*, or *min* as a shorthand for the number value.
```
Wait(1s + 500ms)
Wait
    0.025min
```

## Arrays
Arrays are created, modified, and accessed as in Python notation. Arrays can be nested inside the global/player variables, which allows for more complex operations on arrays. (No slice support yet)

**Creation**
```
empty = []
costs = [5, 15, 30]
```
**Modification**
```
costs[1] = 20
total = costs[0] + costs[1] + costs[2]
```

## Functions
Functions allow you to write a block of code once and reuse it many times. They can be used to generate HUDs like a macro or used as a rule factory. All functions must be defined before they are called, and they must be defined at the top level scope (same as where rules are defined). Parameters can be optional, denoted by `?`, which sets the value to `Null` when omitted. Alternatively, specify a default value e.g. `pos?=Event Player.pos`.

*Note: Functions can access global-scope variables; however, the global scope cannot access variables defined locally in functions*

```
%event_func
    Event
        On Each Player
        All
        All
%add_rule(a, b, name_)
    Rule name_
        event_func()
        c = a + b
%say(text, who?=Everyone) // optional parameter, default to Everyone
    Msg(who, text)
Rule "Function Demo"
    event_func()
    Actions
        say("Thanks!")
add_rule(1, 5, "Add Two")
```
**Builtin Functions**

|Function|Parameters|Description|
|:------:|----------|-----------|
|range|*stop* or *start[, stop[, step]]*|Creates an array of numbers from start to stop (exclusive), counting by step|
|floor|*n*|Rounds a numeric expression down to the nearest integer
|ceil|*n*|Rounds a numeric expression up to the nearest integer
|get_map|Returns the current map ID. This can be compared with map names which alias to their respective ID: `get_map() == Dorado`. For the list of maps and their corresponding IDs, please review [@Xerxes post](https://us.forums.blizzard.com/en/overwatch/t/workshop-resource-map-identifier-map-detection-script-v2-0-only-2-actions/341132).

## Loops
The while loop is syntactic sugar for using the `Loop` action in the Workshop. At the moment, only use while loops if the purpose of the rule is solely to repeat code until a condition is met.
```
while pvar life > 10:
    Damage(Event Player, Null, 10)
```
A for loop lets you iterate over custom iterables, such as an array of values, a range, or workshop values such as All Players.
```
for i in range(1, 10, 2):
    Msg(Event Player, i)
for y in [Genji, Tracer, Widowmaker]:
    Kill
        Players On Hero(y)
```

## Attributes / Methods
Attributes are properties of an object that can be accessed using the dot operator `.`, which refers to the value before it in order to access a property. A method is simply an attribute followed by a call, which has parameters. Refer to the table below for builtin attributes and methods.
```
pvar xpos = Event Player.x // Attribute
y = Victim.jumping and Attacker.moving
scores.append(123) // Method
```

**Attribute Table**

|Name|Description|
|:--:|-----------|
|x|The X component of a vector|
|y|The Y component of a vector|
|z|The Z component of a vector|
|facing|The facing direction of a player|
|pos|The position of a player|
|eyepos|The eye position of a player|
|hero|The hero of a player|
|team|The team of a player|
|jumping|Check if a player is holding the Jump key|
|crouching|Check if a player is holding the Crouch key|
|moving|Check if the speed of a player is non-zero|

**Method Table**

|Name|Parameters|Description|
|:--:|:--------:|-----------|
|append|*element*|Appends an element to the given array|
|index|*element*|Returns the numeric index of an array element|
|halt||Mitigates the motion of a player|

## Alias Table
|Alias|Output|
|-----|------|
|Abs|Absolute Value|
|Any True|Is True For Any|
|All True|Is True For All|
|Chateau Guillard|Château Guillard|
|Cos|Cosine From Degrees|
|Cosr|Cosine From Radians|
|Cur Elem|Current Array Element|
|Filter|Filtered Array|
|Everyone|All Players(Team(All))|
|LOS|Is In Line Of Sight|
|Index|Index Of Array Value|
|Lucio|Lúcio|
|On Each Player|Ongoing - Each Player|
|On Global|Ongoing - Global|
|Players In Radius|Players Within Radius|
|Round|Round To Integer|
|Sin|Sine From Degrees|
|Sinr|Sine From Radians|
|Torbjorn|Torbjörn|

## Imports
OWScript allows bigger scripts and scripts that use common funcitonality to be broken up into modules and imported into a base file. All the "imported" files are evaluated into a parse tree, which is transpiled to workshop code by the base file.

You can import a file by using the `#import 'filepath'`. If the file is in a folder, put the relative path to the file as shown in the examples below:

**Imported File** `lib/functions.owpy`
```
%CreateEffect(pos, type, color)
    Create Effect
        Visible_To: Everyone
        Type: type
        Color: color
        Position: pos
        Radius: 1.5
        Reevaluation: Visible To
```

**Imported File** `src/setup.owpy`
```
Rule "Setup Effects"
    Event
        On Global
    Actions
        CreateEffect(<0,0,0>, Ring, Red)
```

**Base File** `src/game.owpy`
```
#import 'lib/functions'
#import 'src/setup'
```