import sys
from loguru import logger
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import freeze_support
from .gfymu import GfycatMassUploader
from .version import __version__


@logger.catch
def main() -> None:
    if sys.platform.startswith("win"):
        freeze_support()

    print(
        f"""
==================================================
    Gfycat Mass Uploader
    v{__version__}
==================================================
        """
    )

    parser = ArgumentParser()
    parser.add_argument("--configure", action="store_true", help="Re-run first-time setup.")
    parser.add_argument("-t", "--tags", type=str, help="Tags to apply to the GIFs.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search for files to upload recursively.")
    parser.add_argument(
        "-p", "--pattern", type=str, help="If the -r flag is passed, search for files given this glob search pattern."
    )
    parser.add_argument("filepath", metavar="filepath", type=str, help="File/directory path.", nargs="?")
    args = parser.parse_args()

    if args.filepath:
        path = Path(args.filepath).resolve()
    else:
        logger.warning("Filepath was not specified, assuming current directory.")
        path = Path.cwd().resolve()
    tags = args.tags.replace(", ", ",").split(",") if args.tags is not None else []
    gfy = GfycatMassUploader(path, tags, args.recursive, args.pattern)

    if args.configure:
        gfy.setup()

    try:
        gfy.check_valid_files()
        gfy.main()
    except Exception as e:
        logger.error(str(e))


if __name__ == "__main__":
    main()