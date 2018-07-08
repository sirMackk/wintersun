from collections import namedtuple
from pathlib import Path

import pytest

from wintersun import presenters


Post = namedtuple('Post', 'title, standardized_name, template, date, contents')


@pytest.fixture
def atom_presenter_kwargs():
    return {
        'feed_title': 'Feed Title',
        'site_url': 'http://example.com',
        'post_dir': 'posts',
        'author': 'Test Author',
        'encoding': 'utf-8'
    }


class TestAtomPresenter:
    def test_writes_to_path(self, tmpdir, atom_presenter_kwargs):
        target_dir = tmpdir.mkdir('target')
        target_file = 'test_feed'
        target_fpath = Path(target_dir, target_file)

        presenter = presenters.AtomPresenter(**atom_presenter_kwargs)
        presenter.output([], target_fpath)

        assert target_fpath.exists()

    def test_contains_correct_markup(self, tmpdir, mocker,
                                     atom_presenter_kwargs):
        target_dir = tmpdir.mkdir('target')
        target_file = 'test_feed'
        target_fpath = Path(target_dir, target_file)
        post1 = Post('Title', 'title', 'Post', '2018-01-01', 'Lorem ipsum')

        presenter = presenters.AtomPresenter(**atom_presenter_kwargs)
        with mocker.patch.object(
                presenter,
                '_rfc3339_ts_now',
                return_value='2018-01-01T13:03:16-05:00'):
            presenter.output([post1], target_fpath)

        expected_output = """<?xml version="1.0" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Feed Title</title>
    <link href="http://example.com/" rel="self"/>
    <link href="http://example.com" rel="alternate"/>
    <id>http://example.com/</id>
    <updated>2018-01-01T13:03:16-05:00</updated>
    <entry>
        <title>Title</title>
        <link href="http://example.com/posts/title.html" rel="alternate" type="text/html"/>
        <id>http://example.com/posts/title.html</id>
        <published>2018-01-01T00:00:00-05:00</published>
        <updated>2018-01-01T00:00:00-05:00</updated>
        <author>
            <name>Test Author</name>
        </author>
        <content type="html">Lorem ipsum...</content>
    </entry>
</feed>
"""
        with open(target_fpath, 'r') as f:
            assert f.read() == expected_output

    def test_ignores_non_posts(self, tmpdir, mocker, atom_presenter_kwargs):
        target_dir = tmpdir.mkdir('target')
        target_file = 'test_feed'
        target_fpath = Path(target_dir, target_file)
        post1 = Post('Title', 'title', 'Page', '2018-01-01', 'Lorem ipsum')

        presenter = presenters.AtomPresenter(**atom_presenter_kwargs)
        with mocker.patch.object(
                presenter,
                '_rfc3339_ts_now',
                return_value='2018-01-01T13:03:16-05:00'):
            presenter.output([post1], target_fpath)

        expected_output = """<?xml version="1.0" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Feed Title</title>
    <link href="http://example.com/" rel="self"/>
    <link href="http://example.com" rel="alternate"/>
    <id>http://example.com/</id>
    <updated>2018-01-01T13:03:16-05:00</updated>
</feed>
"""
        with open(target_fpath, 'r') as f:
            assert f.read() == expected_output
