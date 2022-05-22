"""Determine full paths for file saving and save files."""
import pathlib
from datetime import datetime, timedelta
from typing import Tuple, Callable

from google.transit import gtfs_realtime_pb2

from . import data


def _calculate_realtime_target(file: data.TransitFile, data_root: pathlib.Path):
    """Calculate a target path for realtime GTFS `file`.

    The sub-path added to `data_root` is based on file category and on a timestamp
    which describes creation time of the file. The path depends only on the contents
    of the file.
    """
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(file.content)
    timestamp = feed.header.timestamp
    server_time = datetime.fromtimestamp(timestamp).isocalendar()
    return data_root.joinpath(
        file.category.value, str(server_time[0]), str(server_time[1]), str(timestamp)
    )


def _calculate_static_targets(file: data.TransitFile, data_root: pathlib.Path):
    """Calculate target paths for static GTFS `file`. (Be careful: coeffects).

    The sub-path added to `data_root` is based on file category and a hash of
    its content. Different paths are generated for one file if the function
    is called during different ISO weeks.

    Return
    ------
    target : pathlib.Path
        Target path where the file should be saved.

    previous_target : pathlib.Path
        `target` path that would be generated in the previous ISO week.
    """
    now = datetime.now()
    iso_now = now.isocalendar()
    iso_previous = (now - timedelta(days=7)).isocalendar()
    filename = hash(file.content)

    target = data_root.joinpath(
        file.category.value, str(iso_now[0]), str(iso_now[1]), str(filename)
    )
    previous_target = data_root.joinpath(
        file.category.value, str(iso_previous[0]), str(iso_previous[1]), str(filename)
    )

    return target, previous_target


def save_files(
    files: Tuple[data.TransitFile],
    data_root: pathlib.Path,
    write_to_disk: Callable[[pathlib.Path, bytes], None],
):
    """Save `files` in a subdirectory of `data_root`."""
    for file in files:
        if file.category != data.TransitCategory.static:
            target = _calculate_realtime_target(file=file, data_root=data_root)
        else:
            target, previous_target = _calculate_static_targets(
                file=file, data_root=data_root
            )
            if previous_target.exists():
                return

        write_to_disk(target, file.content)


def write_to_disk(path: pathlib.Path, content: bytes):
    """Write `content` under `path` and create `path` if necessary.

    Writing function for `save_files`.
    """
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    with path.open("wb") as f:
        f.write(content)
