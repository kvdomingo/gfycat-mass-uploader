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
1. Download the Windows zip through
[releases](https://github.com/kvdomingo/gfycat-mass-uploader/releases).
2. Unzip the contents to a location on your `PATH` to be able to run it from
anywhere.
3. Create a new file named `.env` in the installation directory. 
4. Copy the contents of `.env.example` in this repo and paste it into the
`.env` file you created. Fill in the fields with the needed information.
5. Open a terminal in the directory which contains the files you want to
upload and run:
```cmd
gfycat-mass-upload -t "<tags, comma-separated>"
```

## Using as script
1. Clone the repository.
2. Create a `virtualenv` and install deps from `requirements.txt`
3. Copy the contents of `.env.example` into a new file `.env` and fill
in the fields with the needed information.
4. Run using:
```cmd
python main.py -f <path to file or directory> -t "<tags, comma-separated>"
```
