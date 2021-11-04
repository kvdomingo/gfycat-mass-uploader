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

## Building from source
1. Clone the repository.
2. Create a `virtualenv` and install deps from `requirements.txt`
3. Build executable using:
```cmd
pyinstaller -F -n gfycat-mass-uploader main.py
```
4. A new folder `dist` will be created with the exec inside.
Copy/move this file somewhere on your `PATH` to be able to use
it from any location.
