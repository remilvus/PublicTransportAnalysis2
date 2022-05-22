"""Collect GTFS files."""
import pathlib
import time
from datetime import datetime

from . import downloader, source, persistency


def collect():
    """Collect GTFS files in simplest possible way."""
    transit_downloader = downloader.TransitDownloader(links=downloader.LINKS_BUS_CRACOW)
    transit_source = source.TransitSource(downloader=transit_downloader)
    sleeping_time = 15
    data_root = pathlib.Path("target_path")

    previous_time = datetime.now()
    while True:
        files = transit_source.request_files()
        persistency.save_files(files=files, data_root=data_root)
        delta_time = (datetime.now() - previous_time).total_seconds()
        time.sleep(max(0.0, sleeping_time - delta_time))
        previous_time = datetime.now()
        print(files)


if __name__ == "__main__":
    collect()
