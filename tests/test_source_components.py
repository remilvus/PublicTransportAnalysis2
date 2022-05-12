import datetime
from typing import Callable, Optional, Dict
from unittest import mock

import freezegun
import pytest

import public_transport as pt
import public_transport.collection as ptc
from public_transport.collection import data
from public_transport.utils import CallResult
from public_transport.utils.call_handler import T


CONTENT: Dict[ptc.data.TransitCategory, bytes] = {
    ptc.data.TransitCategory.static: bytes("static", "utf-8"),
    ptc.data.TransitCategory.vehicle_position: bytes("vehicle_positions", "utf-8"),
    ptc.data.TransitCategory.trip_update: bytes("trip_update", "utf-8"),
    ptc.data.TransitCategory.alert: bytes("alerts", "utf-8"),
}


@pytest.fixture
def transit_links():
    return ptc.downloader.TransitUrls(
        static="static.zip",
        trip_updates="updates.pb",
        vehicle_positions="positions.pb",
        alerts="alerts.pb",
    )


@pytest.fixture
def transit_downloader(transit_links):
    class Downloader(ptc.downloader.TransitDownloader):
        def _get_with_etag(
            self, url: str, category: data.TransitCategory
        ) -> Optional[data.TransitFile]:
            return ptc.data.TransitFile(
                etag=self._etags[category],
                content=CONTENT[category],
                category=category,
            )

    return Downloader(links=transit_links)


@pytest.fixture
def transit_downloader_no_files(transit_links):
    class Downloader(ptc.downloader.TransitDownloader):
        def _get_with_etag(
            self, url: str, category: data.TransitCategory
        ) -> Optional[data.TransitFile]:
            return None

    return Downloader(links=transit_links)


@pytest.fixture
def call_handler():
    class Handler(pt.utils.CallHandler):
        def handle_call(self, func: Callable[[], T]) -> CallResult[T]:
            return CallResult(returned_value=func(), success=True, wait_until=None)

    return Handler(break_count=0, break_length=0)


@pytest.fixture
def transit_source(call_handler, transit_downloader):
    source = ptc.source.TransitSource(downloader=transit_downloader)
    source._handler = call_handler
    return source


@pytest.fixture
def transit_source_no_files(call_handler, transit_downloader_no_files):
    source = ptc.source.TransitSource(downloader=transit_downloader_no_files)
    source._handler = call_handler
    return source


@pytest.mark.parametrize("category", list(ptc.data.TransitCategory))
def test_downloader_links(category, transit_links, transit_downloader):
    """Test whether `TransitDownloader` uses correct links for downloading."""
    assert transit_downloader.get_file(category=category).content == CONTENT[category]


def test_source_no_files(transit_source_no_files):
    assert transit_source_no_files.request_files() == tuple()


def test_source_request_files(transit_links, transit_source):
    files = transit_source.request_files()
    assert len(files) == 4
    assert {f.category for f in files} == set(ptc.data.TransitCategory)
    for file in transit_source.request_files():
        assert file.content == CONTENT[file.category]


@pytest.mark.parametrize("category", list(ptc.data.TransitCategory))
def test_etag_update(transit_links, category: ptc.data.TransitCategory):
    downloader = ptc.downloader.TransitDownloader(links=transit_links)

    expected_etag = str(category)
    with mock.patch(
        "public_transport.collection.downloader.requests.get",
        mock.Mock(
            return_value=mock.Mock(status_code=200, headers={"etag": expected_etag})
        ),
    ):
        downloader.get_file(category=category)
        assert downloader._etags[category] == expected_etag
        for other_category, etag in downloader._etags.items():
            if other_category != category:
                assert etag != expected_etag


@freezegun.freeze_time("2021-03-01 12:21:25")
@pytest.mark.parametrize(
    "wait_until, wait_seconds",
    [
        (
            datetime.datetime(
                year=2021,
                month=3,
                day=1,
                hour=12,
                minute=21,
                second=29,
                microsecond=9900,
            ),
            4.0099,
        ),
        (
            datetime.datetime(year=2021, month=3, day=1, hour=12, minute=21, second=0),
            0.0,
        ),
    ],
)
def test_source_wait(transit_source, wait_until, wait_seconds):
    class FailOnce:
        failed = False

        @staticmethod
        def fail_once(_):
            if not FailOnce.failed:
                FailOnce.failed = True
                return pt.utils.CallResult(
                    returned_value=None,
                    success=False,
                    wait_until=wait_until,
                )
            else:
                return pt.utils.CallResult(
                    returned_value=mock.Mock(),
                    success=True,
                    wait_until=None,
                )

    transit_source._handler.handle_call = mock.Mock(side_effect=FailOnce.fail_once)

    with mock.patch(
        "public_transport.collection.source.time.sleep",
        mock.Mock(),
    ) as time_sleep:
        transit_source.request_files()
        time_sleep.assert_called_once_with(wait_seconds)
