# Gfycat Mass Uploader

![GitHub last commit](https://img.shields.io/github/last-commit/kvdomingo/gfycat-mass-uploader?style=for-the-badge)
![GitHub tag (latest SemVer pre-release)](https://img.shields.io/github/v/tag/kvdomingo/gfycat-mass-uploader?include_prereleases&style=for-the-badge)

A small utility to quickly upload all GIFs in a directory
to Gfycat and attach the same set of tags to all of them (no more
manual tagging dozens of GIFs!)

## Features

- Currently can only detect GIFs exported with an `.mp4` file extension.
- Uses multithreading for simultaneous uploads of multiple files.
- Prints the gfycat links after uploads are complete.

## Prerequisites

- Gfycat account
- Gfycat API client ID & secret

## Using as executable

1. Download the Windows/Linux binaries through
   [releases](https://github.com/kvdomingo/gfycat-mass-uploader/releases).
2. Place the executable in a location on your `PATH` to be able to run it from
   anywhere.
3. Open a terminal and run:

```shell
gfycat-mass-upload -t "<tags, comma-separated>" "<path-to-file-or-directory>"
```

The script will automatically determine if the provided path is a file or a
directory. In the latter case, all valid files in the directory will be
uploaded. The path can be omitted if you want all valid files in the current
directory to be uploaded.

If you are running it for the first time, it will prompt you for the necessary
config variables.

## Using as Python module

1. Clone the repository.
2. Install deps:
    ```shell
    poetry install
    ```

3. Run using:
    ```shell
    poetry run python -m gfymu -t "<tags, comma-separated>" <path to file or directory>
    ```

## Building from source

Run:

```shell
task
```

If running on a Linux machine, this will build only for the same CPU architecture. If running on Windows, this will
build for both Windows and Linux.
