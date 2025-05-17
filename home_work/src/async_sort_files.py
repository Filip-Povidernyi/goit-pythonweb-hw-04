import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile, unpack_archive
import argparse
import logging


SORT_FOLDERS = {'images': ('.jpeg', '.png', '.jpg', '.svg', '.tif', '.webp'),
                'videos': ('.mp4', '.avi', '.mov', '.mkv'),
                'audio': ('.mp3', '.wav', '.flac'),
                'documents': ('.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.doc'),
                'archives': ('.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz')
                }


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
    if not logger.hasHandlers():
        logger.addHandler(ch)

    return logger


async def copy_file(file: AsyncPath, adest: AsyncPath) -> None:

    logging_cf = logger_config("INFO", "copy_file")
    try:
        if await file.is_file():

            if file.suffix.lower() in SORT_FOLDERS['images']:
                await copyfile(file, adest / 'images' / file.name)

            elif file.suffix.lower() in SORT_FOLDERS['videos']:
                await copyfile(file, adest / 'videos' / file.name)

            elif file.suffix.lower() in SORT_FOLDERS['audio']:
                await copyfile(file, adest / 'audio' / file.name)

            elif file.suffix.lower() in SORT_FOLDERS['documents']:
                await copyfile(file, adest / 'documents' / file.name)

            elif file.suffix.lower() in SORT_FOLDERS['archives']:
                unpack_dir = adest / 'archives' / file.stem
                await unpack_archive(str(file), str(unpack_dir))

            else:
                await copyfile(file, adest / 'others' / file.name)

        elif await file.is_dir():

            if file.name not in list(SORT_FOLDERS.keys()) + ['others']:
                await read_folder(file, adest)

    except Exception as e:
        logging_cf.error(f"Error while copying {file.name}: {e}")


async def read_folder(apath: AsyncPath, adest: AsyncPath) -> str:

    try:
        for folder in list(SORT_FOLDERS.keys()) + ['others']:
            await (adest / folder).mkdir(exist_ok=True, parents=True)

        async for file in apath.iterdir():

            await copy_file(file, adest)

        return f"All files from {apath} have been copied to the {adest}."

    except Exception as e:
        logging_error = logger_config("ERROR", "read_folder")
        logging_error.error(f"Error while reading folder {apath}: {e}")


async def main():

    logging_info = logger_config("info", "main")

    parser = argparse.ArgumentParser(description="Async file sorter")
    parser.add_argument("source", help="Path to the source folder")
    parser.add_argument("output", nargs='?', default='./sorted_files',
                        help="Path to the output folder")

    args = parser.parse_args()

    apath = AsyncPath(args.source)
    adest = AsyncPath(args.output)
    abs_adest = await adest.absolute()

    if not await apath.exists():
        logging_info.error(f"Path {apath} does not exist.")
        return

    if not await adest.exists():
        await adest.mkdir(parents=True, exist_ok=True)
        logging_info.info(f"Output folder {abs_adest} created.")

    logging_info.info(await read_folder(apath, adest))

    logging_info.info(f"Source folder {apath}")
    logging_info.info(f"Destination folder {abs_adest}")


if __name__ == "__main__":
    asyncio.run(main())
