"""Collect GTFS files."""
import argparse
import pathlib
import time
from datetime import datetime
from typing import Union

from . import downloader, source, persistence


def collect(
    source_urls: downloader.TransitUrls,
    data_root: Union[str, pathlib.Path],
    waiting_time: float,
):
    """Download files from `source_urls` and save them under `data_root`.

    Arguments
    ---------
    source_urls : downloader.TransitUrls
        Urls under which static and real-time GTFS files are published.

    data_root : Union[str, pathlib.Path]
        A path under which files will be stored.

    waiting_time : float
        Minimum amount of time between consequent downloading attempts.
    """
    transit_downloader = downloader.TransitDownloader(urls=source_urls)
    transit_source = source.TransitSource(downloader=transit_downloader)
    data_root = pathlib.Path(data_root)

    previous_time = datetime.now()
    while True:
        files = transit_source.request_files()
        persistence.save_files(
            files=files, data_root=data_root, write_to_disk=persistence.write_to_disk
        )
        delta_time = (datetime.now() - previous_time).total_seconds()
        time.sleep(max(0.0, waiting_time - delta_time))
        previous_time = datetime.now()


if __name__ == "__main__":
    allowed_sources = tuple(downloader.URLS.keys())

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        metavar="S",
        type=str,
        help="Source of GTFS files.",
        choices=allowed_sources,
    )
    parser.add_argument(
        "data_path", metavar="P", help="Path where GTFS files will be saved."
    )
    parser.add_argument(
        "--wait",
        metavar="W",
        type=float,
        nargs="?",
        default=30.0,
        help="Waiting time between consequent downloads.",
    )

    args = parser.parse_args()
    print(args)
    collect(
        source_urls=downloader.URLS[args.source],
        data_root=args.data_path,
        waiting_time=args.wait,
    )
