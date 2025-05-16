import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile, unpack_archive
import argparse
import logging


SORT_FOLDERS = {'images', 'videos', 'audio', 'documents', 'archives', 'others'}


def logger_config(level: str, name: str) -> logging.Logger:

    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = levels.get(level.upper())
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


async def copy_file(file: AsyncPath, apath: AsyncPath) -> None:

    logging_cf = logger_config("INFO", "copy_file")
    try:
        if await file.is_file():

            if file.suffix.lower() in ('.jpeg', '.png', '.jpg', '.svg', '.tif', 'webp'):
                await copyfile(file, apath / 'images' / file.name)
                logging_cf.info(f"Copied {file.name} to {apath / 'images'}")

            elif file.suffix.lower() in ('.mp4', '.avi', '.mov', '.mkv'):
                await copyfile(file, apath / 'videos' / file.name)
                logging_cf.info(f"Copied {file.name} to {apath / 'videos'}")

            elif file.suffix.lower() in ('.mp3', '.wav', '.flac'):
                await copyfile(file, apath / 'audio' / file.name)
                logging_cf.info(f"Copied {file.name} to {apath / 'audio'}")

            elif file.suffix.lower() in ('.pdf', '.docx', '.txt'):
                await copyfile(file, apath / 'documents' / file.name)
                logging_cf.info(
                    f"Copied {file.name} to {apath / 'documents'}")

            elif file.suffix.lower() in ('.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz'):
                unpack_dir = apath / 'archives' / file.stem
                await unpack_archive(str(file), str(unpack_dir))
                logging_cf.info(f"Unpacked {file.name} to {unpack_dir}")

            else:
                await copyfile(file, apath / 'others' / file.name)
                logging_cf.info(f"Copied {file.name} to {apath / 'others'}")

        elif await file.is_dir():

            if file.name not in SORT_FOLDERS:

                new_path = apath / file.name
                await read_folder(new_path)
    except Exception as e:
        logging_cf.error(f"Error while copying {file.name}: {e}")


async def read_folder(apath: AsyncPath) -> str:

    try:
        for folder in SORT_FOLDERS:
            await (apath / folder).mkdir(exist_ok=True, parents=True)

        async for file in apath.iterdir():

            await copy_file(file, apath)

        return f"All files from {apath} have been copied to the appropriate folders."

    except Exception as e:
        logging_error = logger_config("ERROR", "read_folder")
        logging_error.error(f"Error while reading folder {apath}: {e}")


async def main():

    logging_info = logger_config("info", "main")

    parser = argparse.ArgumentParser(description="Async file sorter")
    parser.add_argument("source", help="Path to the source folder")
    args = parser.parse_args()

    apath = AsyncPath(args.source)

    if not await apath.exists():
        logging_info.error(f"Path {apath} does not exist.")
        return

    logging_info.info(await read_folder(apath))


if __name__ == "__main__":
    asyncio.run(main())
