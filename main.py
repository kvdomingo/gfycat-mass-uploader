import sys
import warnings
from pathlib import Path
from argparse import ArgumentParser
from multiprocessing import freeze_support
from gfymu import GfycatMassUploader


def main() -> None:
    if sys.platform.startswith("win"):
        freeze_support()

    parser = ArgumentParser()
    parser.add_argument("--configure", action="store_true", help="Re-run first-time setup.")
    parser.add_argument("-t", "--tags", type=str, help="Tags to apply to the GIFs.")
    parser.add_argument("filepath", metavar="filepath", type=str, help="File/directory path.", nargs="?")
    args = parser.parse_args()

    if args.filepath:
        path = Path(args.filepath).resolve()
    else:
        warnings.warn(
            "Filepath was not specified, assuming current directory.",
            category=RuntimeWarning,
        )
        path = Path().resolve()
    tags = args.tags.replace(", ", ",").split(",") if args.tags is not None else []
    gfy = GfycatMassUploader(path, tags)
    if args.configure:
        gfy.setup()

    try:
        gfy.check_valid_files()
        gfy.main()
    except Exception as e:
        print(f"{e}\n")


if __name__ == "__main__":
    main()
