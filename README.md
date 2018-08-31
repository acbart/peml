# PEML: The Program Exercise Markup Language

This repository contains the **"peml" python module**, a parser for PEML.

The **Programming Exercise Markup Language (PEML)** (feedback on
name choice is welcome!) is intended to be a simple, easy format for
CS and IT instructors of all kinds (college, community college, high
school, whatever) to describe programming assignments and activities.
We want it to be so easy (and obvious) to use that instructors won't
see it as a technological or notational barrier to expressing their
assignments.

We intend for this format to be something that authors of automated
grading tools can adopt, so they can provide a very easy, low-energy
onboarding path for existing instructors to get programming activities
into such tools. As a result, this notation leans heavily on supporting
authors and streamlining common cases, even if this may require more
work on the part of tool developers--the goal is to make it super easy
for **authors** of programming activities, not to fit into a specific
auto-grader or simplify tasks for tool writers.

For full details on PEML, see:

http://CSSPLICE.github.io/peml/

## Installation

    pip install peml-python

## Usage

```
import peml

peml.load("string containing a PEML description")
# nested hash representation of exercise

peml.load_file("file_name.peml")
# nested has representation of the exercise
```

Eventually, we'll also add support for:

```
import peml

peml.dump(some_nested_data)
# string containing exercise rendered in PEML format

```

... but these don't work yet.

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/acbart/peml-python.
