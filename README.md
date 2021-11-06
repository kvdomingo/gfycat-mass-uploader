# Gfycat Mass Uploader

A small utility to quickly upload all GIFs in a directory 
to Gfycat and attach the same set of tags to all of them (no more
manual tagging dozens of GIFs!)

## Features
- Currently can only detect GIFs exported with an `.mp4` file extension. 
- Uses multithreading for simultaneous uploads of multiple files.

## Installation
Windows binaries are available through
[releases](https://github.com/kvdomingo/gfycat-mass-uploader/releases).

## Running as script
1. Clone the repository.
2. Create a `virtualenv` and install deps from `requirements.txt`
3. Use like a normal script using:
```cmd
python main.py -f <path to file or directory> -t "<tags, comma-separated>"
```
