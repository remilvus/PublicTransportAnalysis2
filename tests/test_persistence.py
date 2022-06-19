import datetime
import pathlib
from unittest import mock

import freezegun
import pytest

import public_transport.collection as ptc

TIMESTAMP = 1652638589
AFTER_TIMESTAMP = TIMESTAMP + 10000
TIMESTAMP_MOCK = mock.Mock(
    return_value=mock.Mock(header=mock.Mock(timestamp=TIMESTAMP))
)


@mock.patch(
    "public_transport.collection.persistence.gtfs_realtime_pb2.FeedMessage",
    TIMESTAMP_MOCK,
)
@mock.patch(
    "public_transport.collection.persistence.pathlib.Path.exists",
    mock.Mock(return_value=False),
)
def test_each_file_saved_once():
    files = tuple(
        ptc.data.TransitFile(
            category=category, content=bytes(category.value, "utf-8"), etag=""
        )
        for category in ptc.data.TransitCategory
    )
    was_saved = {
        bytes(category.value, "utf-8"): 0 for category in ptc.data.TransitCategory
    }

    def save_file(_: pathlib.Path, content: bytes):
        was_saved[content] += 1

    ptc.persistence.save_files(
        files=files, data_root=pathlib.Path("/dev/null/"), write_to_disk=save_file
    )

    for save_count in was_saved.values():
        assert save_count == 1


@mock.patch(
    "public_transport.collection.persistence.gtfs_realtime_pb2.FeedMessage",
    TIMESTAMP_MOCK,
)
@mock.patch(
    "public_transport.collection.persistence.pathlib.Path.exists",
    mock.Mock(return_value=True),
)
def test_static_saved_once():
    """Test static file saving, when the file already exists."""
    files = (
        ptc.data.TransitFile(
            category=ptc.data.TransitCategory.static,
            content=bytes(ptc.data.TransitCategory.static.value, "utf-8"),
            etag="",
        ),
    )

    def save_file(_: pathlib.Path, __: bytes):
        assert False

    ptc.persistence.save_files(
        files=files, data_root=pathlib.Path("/dev/null/"), write_to_disk=save_file
    )


@freezegun.freeze_time(datetime.datetime.fromtimestamp(AFTER_TIMESTAMP))
@mock.patch(
    "public_transport.collection.persistence.gtfs_realtime_pb2.FeedMessage",
    TIMESTAMP_MOCK,
)
@mock.patch(
    "public_transport.collection.persistence.pathlib.Path.exists",
    mock.Mock(return_value=False),
)
@pytest.mark.parametrize("category", list(ptc.data.TransitCategory))
def test_saving_path(category: ptc.data.TransitCategory):
    files = (
        ptc.data.TransitFile(
            category=category, content=bytes(category.value, "utf-8"), etag=""
        ),
    )
    data_root = pathlib.Path("/my/storage/").resolve()

    def save_file(path: pathlib.Path, _: bytes):
        path_string = str(path.resolve())

        assert path_string.startswith(str(data_root))
        assert category.value in path_string
        assert "2022/19" in path_string
        if category == ptc.data.TransitCategory.static:
            assert path_string.endswith(str(hash(bytes(category.value, "utf-8"))))
        else:
            assert path_string.endswith(str(TIMESTAMP))

    ptc.persistence.save_files(
        files=files, data_root=data_root, write_to_disk=save_file
    )
