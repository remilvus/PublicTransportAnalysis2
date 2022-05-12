"""Safe and generic interactions with a source of GTFS files."""
import time
import typing
from datetime import datetime
from typing import Tuple, List, Optional

from . import data
from . import downloader
import public_transport.utils as ptu


class TransitSource:
    """Wrapper of GTFS-source related data and utilities."""

    def __init__(self, downloader: downloader.TransitDownloader):
        self._handler = ptu.CallHandler(break_count=5, break_length=120.0)
        self._downloader = downloader

    def request_files(self) -> Tuple[data.TransitFile]:
        """Download all new GTFS files.

        New files are understood as those which changed their etags since the last
        download.
        """
        result = self._handler.handle_call(self._download_files)
        while not result.success:
            if result.wait_until is None:
                raise AssertionError(
                    "Wait value must be specified when `success` is False"
                )
            time.sleep(max(0.0, (result.wait_until - datetime.now()).total_seconds()))
            result = self._handler.handle_call(self._download_files)

        if result.returned_value is None:
            raise AssertionError(
                "Returned value must be specified when `success` is True"
            )
        return result.returned_value

    def _download_files(self) -> Tuple[data.TransitFile]:
        files: List[Optional[data.TransitFile]] = [
            self._downloader.get_file(category=category)
            for category in data.TransitCategory
        ]
        return typing.cast(
            Tuple[data.TransitFile], tuple(f for f in files if f is not None)
        )
