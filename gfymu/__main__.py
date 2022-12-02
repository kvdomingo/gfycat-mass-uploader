import sys
from argparse import ArgumentParser
from multiprocessing import freeze_support
from pathlib import Path

from loguru import logger

from . import __version__
from .gfymu import GfycatMassUploader


@logger.catch
def main() -> None:
    if sys.platform.startswith("win"):
        freeze_support()

    parser = ArgumentParser()
    parser.add_argument("--configure", action="store_true", help="Re-run first-time setup.")
    parser.add_argument("-v", "--version", action="store_true", help="Show program version.")
    parser.add_argument("-t", "--tags", type=str, help="Tags to apply to the GIFs.")
    parser.add_argument("-p", "--pattern", type=str, help="Search for files given this glob search pattern.")
    parser.add_argument("filepath", metavar="filepath", type=str, help="File/directory path.", nargs="?")
    args = parser.parse_args()

    if not len(sys.argv) > 1:
        parser.print_help()
        return

    if args.filepath:
        path = Path(args.filepath).resolve()
    else:
        path = Path.cwd().resolve()
    tags = args.tags.replace(", ", ",").split(",") if args.tags is not None else []
    gfy = GfycatMassUploader(path, tags, args.pattern)

    if args.version:
        print(__version__)
        return

    print(
        f"""
    ==================================================
        Gfycat Mass Uploader
        v{__version__}
    ==================================================
        """
    )

    if args.configure:
        gfy.setup()

    try:
        gfy.check_valid_files()
        gfy.main()
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
