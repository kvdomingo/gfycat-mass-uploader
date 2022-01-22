![GitHub last commit](https://img.shields.io/github/last-commit/kvdomingo/gfycat-mass-uploader?style=for-the-badge)

# Gfycat Mass Uploader

A small utility to quickly upload all GIFs in a directory 
to Gfycat and attach the same set of tags to all of them (no more
manual tagging dozens of GIFs!)

## Features
- Currently can only detect GIFs exported with an `.mp4` file extension. 
- Uses multithreading for simultaneous uploads of multiple files.

## Prerequisites
- Gfycat account
- Gfycat API client ID & secret

## Using as executable
1. Download the Windows binary through
[releases](https://github.com/kvdomingo/gfycat-mass-uploader/releases).
2. Place the executable in a location on your `PATH` to be able to run it from
anywhere. 
3. Open a terminal and run:
```cmd
gfycat-mass-upload -t "<tags, comma-separated>" "<path-to-file-or-directory>"
```
The script will automatically determine if the provided path is a file or a
directory. In the latter case, all valid files in the directory will be
uploaded. The path can be omitted if you want all valid files in the current
directory to be uploaded.

If you are running it for the first time, it will prompt you for the necessary
config variables.

## Using as script
1. Clone the repository.
2. Create a `virtualenv` and install deps from `requirements.txt`
3. Copy the contents of `.env.example` into a new file `.env` and fill
in the fields with the needed information.
4. Run using:
```cmd
python main.py -t "<tags, comma-separated>" <path to file or directory>
```
