# Lab Pair Generator

Creates randomized pairs of students.

## The Problem

1. Creating random pairs of students multiple times in a row often results in
many repeat pairings before everyone has had a chance to work with everyone
else.

2. Absent students shouldn't be included in any of the pairs for the day.

3. If there's an odd number of students there should be one group of three.

4. Data should be kept separate for each cohort/class.

## The Solution

1. For each student, keep track of the number of times they've been paired with
every other student and use that number as a weight in the random pair
selection process.

2. A set of unavailable students is added to as the pairs are being generated,
so absent students can be added to the set before selection even begins.

3. The group of three is selected first. First, the student with with smallest
sum of total past pairings is selected. This student is likely to be the one
who has been in the fewest groups of three so far (though they could also have
been absent the most). Then, a partner for the first student is found by the
normal, weighted method. Finally, a third student is found based on the lowest
sum of past pairings for the whole group of three.

4. An instance of the custom `Cohort` class is created for each cohort/class,
which has methods for generating pairs as well as persisting the data via
`pickle`.

## The Application

This project started in the `main` branch, but has since been broken into
two parts:

For the CLI tool, check out the
[:twisted_rightwards_arrows: cli branch](https://github.com/caseinpoint/lab_partners/tree/cli)

For the web app, check out the
[:twisted_rightwards_arrows: webapp branch](https://github.com/caseinpoint/lab_partners/tree/webapp)

You can see the web app deployed on pythonanywhere
[here](http://caseinpoint.pythonanywhere.com/). :bangbang: Please note that
this tool may still be in use by others, so only mess around with the
[example cohort](http://caseinpoint.pythonanywhere.com/cohorts/example), or
[create a new one](http://caseinpoint.pythonanywhere.com/new). Thanks!

## CLI Tool

### Installation

You will need `git` and `Python 3` installed.

__1. Clone this branch to your local machine:__

HTTPS:
```
git clone --single-branch --branch cli https://github.com/caseinpoint/lab_partners.git
```

SSH:
```
git clone --single-branch --branch cli git@github.com:caseinpoint/lab_partners.git
```

__2. For ease of use, make the symlink file `pair` executable:__

```
chmod +x pair
```
This will allow you to run `./pair` in the terminal, instead of
`python3 pairs.py`.

### Setup

This tool requires a JSON file for each class/cohort with an array of names to
be saved in `./data/json`. To make the names parsable in the command line, make
sure that they don't include any spaces or special characters. If you have more
than one student with the same name, make sure to include initials or nicknames
to tell them apart. Duplicates will get overridden. See the included
[example.json](./data/json/example.json).

### Usage

This tool has been built with the
[argparse](https://docs.python.org/3.10/library/argparse.html) module. To see
usage and options run
```
./pair --help
```
or `./pair -h`.
