"""tests for console renders (TextRenderer, JsonRenderer)"""

import json
import pytest

from rss_reader.rss_reader import TextRenderer, JsonRenderer
from tests.helpers import read_test_data

TEXT_RENDERER = "text"
JSON_RENDERER = "json"


@pytest.fixture(
    name="renderer_type",
    params=[
        pytest.param(TEXT_RENDERER, id="TextRenderer"),
        pytest.param(JSON_RENDERER, id="JsonRenderer"),
    ],
)
def fixture_renderer_type(request):
    """
    A fixture for all supported renders
    """
    return request.param


@pytest.mark.parametrize(
    "data,expected_j,expected_t",
    [
        pytest.param({"other": "other"}, '[{"entries": []}]\n', "", id="empty"),
        pytest.param(
            {"title": "test"},
            '[{"title": "test", "entries": []}]\n',
            "Feed: test\n",
            id="exact",
        ),
        pytest.param(
            {"title": "test", "other": "other"},
            '[{"title": "test", "entries": []}]\n',
            "Feed: test\n",
            id="reduced",
        ),
    ],
)
def test_renderer_feed_start(renderer_type, data, expected_j, expected_t, capfd):
    """
    Tests render_feed_start in renders
    """
    if renderer_type == JSON_RENDERER:
        renderer = JsonRenderer()
        expected = expected_j
    elif renderer_type == TEXT_RENDERER:
        renderer = TextRenderer()
        expected = expected_t
    renderer.render_feed_start(data)
    renderer.render_feed_end()
    renderer.render_exit()
    out, _ = capfd.readouterr()

    if renderer_type == JSON_RENDERER:
        assert json.loads(out)

    assert out == expected


@pytest.mark.parametrize(
    "data,expected_j,expected_t",
    [
        pytest.param({"other": "other"}, '[{"entries": []}]\n', "", id="empty"),
        pytest.param(
            {"title": "test"},
            '[{"entries": [{"title": "test"}]}]\n',
            "\n\nTitle: test\n\n",
            id="title",
        ),
        pytest.param(
            {"title": ""},
            '[{"entries": [{"title": ""}]}]\n',
            "\n\nTitle: \n\n",
            id="title_len_0",
        ),
        pytest.param(
            {"title": "test'&#x27;&nbsp;&#160;\u2019\u00a0", "other": "other"},
            '[{"entries": [{"title": "test\'\'  \\u2019"}]}]\n',
            "\n\nTitle: test''  ???\n\n",
            id="title_reduced",
        ),
        pytest.param(
            {"published": "2020-01-02"},
            '[{"entries": [{"published": "2020-01-02"}]}]\n',
            "Date: 2020-01-02\n",
            id="published",
        ),
        pytest.param(
            {"link": "http://one.com"},
            '[{"entries": [{"link": "http://one.com"}]}]\n',
            "Link: http://one.com\n",
            id="link",
        ),
        pytest.param(
            {"description": "Test news"},
            '[{"entries": [{"description": "Test news"}]}]\n',
            "\nTest news\n",
            id="description",
        ),
        pytest.param(
            {
                "title": "test",
                "published": "2020-01-02",
                "link": "http://many.com",
                "description": "Test news",
            },
            '[{"entries": [{"title": "test", "published": "2020-01-02", "link": '
            + '"http://many.com", "description": "Test news"}]}]\n',
            "\n\nTitle: test\n\nDate: 2020-01-02\nLink: http://many.com\n\nTest news\n",
            id="all",
        ),
    ],
)
def test_renderer_feed_entry(renderer_type, data, expected_j, expected_t, capfd):
    """
    Tests render_feed_entry in renders
    """
    if renderer_type == JSON_RENDERER:
        renderer = JsonRenderer()
        expected = expected_j
    elif renderer_type == TEXT_RENDERER:
        renderer = TextRenderer()
        expected = expected_t
    renderer.render_feed_entry(data)
    renderer.render_feed_end()
    renderer.render_exit()
    out, _ = capfd.readouterr()

    if renderer_type == JSON_RENDERER:
        assert json.loads(out)

    assert out == expected


@pytest.mark.parametrize(
    "file_name",
    [
        pytest.param("data_simple", id="simple"),
    ],
)
def test_json_renderer_entry_description(file_name, capfd):
    """
    Tests render_entry with a real HTML content in JsonRenderer
    """
    input_data = read_test_data(f"{file_name}.html")
    expected = read_test_data(f"{file_name}_json.txt")
    renderer = JsonRenderer()
    renderer.render_feed_entry({"description": input_data})
    renderer.render_feed_end()
    renderer.render_exit()
    out, _ = capfd.readouterr()

    assert json.loads(out)

    assert out == expected


@pytest.mark.parametrize(
    "header,entries,expected_j,expected_t",
    [
        pytest.param(
            {"title": "feed for test"},
            [
                {
                    "title": "item 1",
                    "published": "2020-01-02",
                    "link": "http://somewhere.com/news1",
                    "description": "something happened",
                },
                {
                    "title": "item 2",
                    "published": "2021-01-02",
                    "link": "http://somewhere.com/news2",
                    "description": "something new happened",
                },
            ],
            '[{"title": "feed for test", "entries": [{"title": "item 1", "published": '
            + '"2020-01-02", "link": "http://somewhere.com/news1", "description": '
            + '"something happened"}, {"title": "item 2", "published": "2021-01-02", '
            + '"link": "http://somewhere.com/news2", "description": '
            + '"something new happened"}]}]\n',
            "Feed: feed for test\n\n\nTitle: item 1\n\nDate: 2020-01-02\nLink: "
            + "http://somewhere.com/news1\n\nsomething happened\n\n\nTitle: item 2\n"
            + "\nDate: 2021-01-02\nLink: http://somewhere.com/news2\n\nsomething new"
            + " happened\n",
            id="two",
        ),
    ],
)
# pylint: disable=too-many-arguments
def test_renderer_full(renderer_type, header, entries, expected_j, expected_t, capfd):
    """
    Tests render_entry in renders
    """
    if renderer_type == JSON_RENDERER:
        renderer = JsonRenderer()
        expected = expected_j
    elif renderer_type == TEXT_RENDERER:
        renderer = TextRenderer()
        expected = expected_t
    renderer.render_feed_start(header)
    for entry in entries:
        renderer.render_feed_entry(entry)
    renderer.render_feed_end()
    renderer.render_exit()
    out, _ = capfd.readouterr()

    if renderer_type == JSON_RENDERER:
        assert json.loads(out)

    assert out == expected
