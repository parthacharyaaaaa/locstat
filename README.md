# locstat
## Get source code line statistics quickly

* [Installation](#installation)
* [Usage](#usage)
    * [Primary Action](#primary-action)
    * [Parsing Filters](#parsing-filters)
    * [Finer Parsing Control](#finer-parsing-controls)
    * [Emitting Results](#emitting-results)

* [Examples](#usage)

* [Customizations](#customizations)
* [License](#license)
* [Comptatibility Notes](#compatibility-notes)
* [Acknowledgements](#acknowledgements)

## Installation

```bash
$ pip install locstat
```

## Usage
locstat is designed to be a CLI tool, invocable as the package name itself.

```bash
$ locstat [-h] (-v VERSION | -c CONFIG | -f FILE | -d DIR) [options]
```

### Primary Action
A primary action must be specified when invoking the tool through the command line, namely:
* **-v/--version**: Display the installed version and exit
* **-h/--help**: Display the help message and exit
* **-c/--config**: Display and optionally edit the configuration settings and exit

* **-f/--file**: Filepath to parse
* **-d/--dir**: Directory to parse

Note: These options are **mutually exclusive**

### Parsing Filters:
#### Directories:
**-xd/--exclude-dir**: Directory paths following this flag will be ignored.

**-id/--include-dir**: Parse only the directories following this flag.

#### Files:
**-xf/--exclude-file**: Filepaths following this flag will be ignored.

**-if/--include-file**: Only filepaths following this flag will be parsed.

**-xt/--exclude-type**: File extensions following this flag will be ignored.

**-it/--include-type**: Only file extensions following this flag will be parsed.

### Finer Parsing Controls
**-pm/--parsing-mode**: Override default file parsing behaviour. Available options: MMAP, BUF, COMP.

**BUF**: Default parsing mode. Allocates a buffer of 4MB and reads files in chunks into this buffer.

**MMAP**: Map files to the virtual memory of the locstat process in an attempt to reduce the number of syscalls. May improve performance for hot page caches or for larger source files. Uses `mmap` and `madvice` on Linux and Mac systems, or `CreateFileMapping` and `MapViewOfFile` on Windows.

**COMP**: Read the entire file at once without any buffering.

**-vb/--verbosity**: Amount of statistics to include in the final report. Available modes:

BARE: Default mode, count only total lines and lines of code.

REPORT: Additionally include language metadata, i.e. number of files, total lines, and lines of code per file extension parsed.

DETAILED: Additionally include language metadata and per directory and per file line statistics.

**-md/--max-depth**: Recursively scan sub-directories upto the given level. Negative values are treated as infinite depth. Defaults to -1

**-mc/--min-chars**: Specify the minimum number of non-whitespace characters a line should have to be considered an LOC. Defaults to 1.

### Emitting Results
**-o/--output**: Specify output file to dump counts into. If not specified, output is dumped to `stdout`. If output file is in json then output is formatted differently.

## Examples
Let's run locstat against a cloned repository of `cpython-main`

```bash
$ locstat -d /home/tcn/targets/cpython-main/

GENERAL:
total : 2155349
loc : 1722995
time : 0.913s
scanned_at : 19/02/26, at 16:05:11
platform : Linux
```

Additionally, we can fetch per-extension metadata using the `REPORT` verbosity mode.

```bash
$ locstat -d /home/tcn/targets/cpython-main/ -vb REPORT

GENERAL:
total : 2155349
loc : 1722995
time : 0.204s
scanned_at : 19/02/26, at 16:06:15
platform : Linux

LANGUAGE METADATA
Extension  Files    Total     LOC
---------------------------------
py          2211  1088097  851618
bat           32     2327    1959
ps1            6      571     451
sh            14      918     582
css            6     3248    2570
c            485   652306  498587
h            637   356061  319201
js            10     2431    1775
html          18    10327    9132
xml          119    31796   31615
m             10     1029     807
xsl            2       33      16
cpp            7     4989    3796
vbs            1        1       0
pyi            1        4       2
asm            1       46      18
lisp           1      692     502
ts             2       37      32
kts            3      307     236
kt             2      129      96
```
**Note**: The drop in scanning time in the second example is thanks to page caching following the first example.

## Customizations
locstat allows for default behaviour to be overridden per invocation, such as:

```bash
locstat -f foo.py --min-chars 2
```
This overrides the default minimum characters threshold of 1

Furthermore, changes to default values can be saved permanently using the `--config` (shorthand: `-c`) flag.

When invoked without any arguments, `--config` displays the current default configurations for locstat.

```bash
$ locstat --config
max_depth : -1
minimum_characters : 1
parsing_mode : BUF
verbosity : BARE
```

To update any value, append the flag with the option name and it's new value as a space-separated pair.

```bash
$ locstat --config max_depth 5 parsing_mode MMAP verbosity report
$ locstat --config
max_depth : 5
minimum_characters : 1
parsing_mode : MMAP
verbosity : REPORT
```

**Note**: String enums are case-insensitive.

## License
locstat is licensed under the MIT license.

## Compatibility Notes
locstat ships using `cibuildwheels`, allowing for platform-specific wheels for Linux, Windows, and Mac, spanning different architectures.

However, some platforms have been excluded due to cross-compatibility pains or their packaging requiring extremely long waiting times for workflow runners (such as Mac systems using Intel chips).

This does not mean that locstat is completely incompatible on all remaining systems. The source distribution is also shipped alongside wheels.

## Acknowledgements
locstat (formerly named pycloc, but that name was taken 2 weeks before I got to publishing :P) started as a one-day project to allow a good friend to count how many lines of C++ code were present in his UE5 project.

Since then, many features and improvements have been added to this still simple tool, all of which would have been impossible without the collective effort of thousands of open-source contributors, spanning across many projects such as CPython and Perl Cloc (the gold standard!) to even make programming possible for me. 

Furthermore, the online help provided by thousands of contributors on StackOverflow, HackerNews and countless personal technical blogs has made it possible for me to polish and refine this tool.

My deepest gratitude goes to everyone, however indirectly involved, in the sphere of computer programming. Even for the smallest steps I take, I stand nonetheless on the shoulders of countless giants.