from datetime import UTC, datetime, timedelta
from io import BytesIO

import pytest
from PIL import Image

from custom_components.tideglass.graph import render_graph
from custom_components.tideglass.model import height_at, local_window, parse_predictions, select_tides

from .conftest import SETTINGS


def test_exact_turning_point(predictions):
    events, _ = predictions
    tide = events[4]
    before = select_tides(events, tide.time - timedelta(seconds=1))
    at = select_tides(events, tide.time)
    assert before["next"] == tide
    assert at["last"] == tide
    assert at["next"].time > tide.time


@pytest.mark.parametrize(("day", "hours"), [("2026-03-08", 23), ("2026-11-01", 25)])
def test_dst_days(day, hours):
    now = datetime.fromisoformat(day + "T16:00:00+00:00")
    begin, end = local_window(now, "America/New_York")
    assert (end - begin).total_seconds() == hours * 3600


@pytest.mark.parametrize("bad", ["NaN", "Infinity", "bad", ""])
def test_reject_invalid_heights(bad):
    with pytest.raises(ValueError):
        parse_predictions({"predictions": [{"t": "2026-09-27 12:00", "v": bad}]}, events=False)


def test_interpolation_and_no_extrapolation(predictions):
    _, samples = predictions
    a, b = samples[:2]
    assert height_at(samples, a.time) == a.height
    assert height_at(samples, a.time + (b.time - a.time) / 2) == pytest.approx((a.height + b.height) / 2)
    assert height_at(samples, a.time - timedelta(seconds=1)) is None
    assert height_at(samples, samples[-1].time + timedelta(seconds=1)) is None


@pytest.mark.parametrize(("theme", "days"), [("light", 1), ("dark", 1), ("light", 7), ("dark", 7)])
def test_graphs_are_real_pngs(predictions, theme, days):
    data = render_graph(*predictions, datetime(2026, 9, 27, 17, tzinfo=UTC), SETTINGS, theme, days)
    im = Image.open(BytesIO(data))
    assert im.size == (1200, 650)
    assert im.format == "PNG"


def test_subordinate_station_has_no_fake_height(predictions):
    events, _ = predictions
    assert height_at((), datetime(2026, 9, 27, 17, tzinfo=UTC)) is None
    assert render_graph(events, (), datetime(2026, 9, 27, 17, tzinfo=UTC), SETTINGS).startswith(b"\x89PNG")
