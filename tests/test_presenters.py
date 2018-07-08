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


@pytest.fixture
def post():
    return Post('Post-Title', 'post-title', 'Post', '2018-01-01', 'Lorem ipsum')


@pytest.fixture()
def template_dir(tmpdir):
    template_dir = tmpdir.mkdir('templates')
    index_template = template_dir.join('index.html')
    post_template = template_dir.join('post.html')

    index_template.write('<h1>Index</h1>'
                         '{% for page in pages %}'
                         '{{ page.title }}'
                         '{% endfor %}')

    post_template.write('<h1>{{ title }}</h1>'
                        '<h2>{{ date }}</h2>'
                        '{{ contents }}')
    return template_dir


class TestAtomPresenter:
    def test_writes_to_path(self, tmpdir, atom_presenter_kwargs):
        target_dir = tmpdir.mkdir('target')
        target_file = 'test_feed'
        target_fpath = Path(target_dir, target_file)

        presenter = presenters.AtomPresenter(**atom_presenter_kwargs)
        presenter.output([], target_fpath)

        assert target_fpath.exists()

    def test_contains_correct_markup(self, tmpdir, mocker,
                                     atom_presenter_kwargs, post):
        target_dir = tmpdir.mkdir('target')
        target_file = 'test_feed'
        target_fpath = Path(target_dir, target_file)

        presenter = presenters.AtomPresenter(**atom_presenter_kwargs)
        with mocker.patch.object(
                presenter,
                '_rfc3339_ts_now',
                return_value='2018-01-01T13:03:16-05:00'):
            presenter.output([post], target_fpath)

        expected_output = """<?xml version="1.0" ?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Feed Title</title>
    <link href="http://example.com/" rel="self"/>
    <link href="http://example.com" rel="alternate"/>
    <id>http://example.com/</id>
    <updated>2018-01-01T13:03:16-05:00</updated>
    <entry>
        <title>Post-Title</title>
        <link href="http://example.com/posts/post-title.html" rel="alternate" type="text/html"/>
        <id>http://example.com/posts/post-title.html</id>
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

    def test_ignores_non_posts(self, tmpdir, mocker, atom_presenter_kwargs,
                               post):
        target_dir = tmpdir.mkdir('target')
        target_file = 'test_feed'
        target_fpath = Path(target_dir, target_file)
        post = post._replace(template='Page')

        presenter = presenters.AtomPresenter(**atom_presenter_kwargs)
        with mocker.patch.object(
                presenter,
                '_rfc3339_ts_now',
                return_value='2018-01-01T13:03:16-05:00'):
            presenter.output([post], target_fpath)

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


class TestHTMLPresenter:
    def test_outputs_index_file(self, tmpdir, post, template_dir):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'posts')
        presenter = presenters.HTMLPresenter(template_dir)

        presenter.output([post], target_dir)

        index_fpath = target_dir.absolute().parent / 'posts.html'
        assert index_fpath.exists()
        with open(index_fpath, 'r') as f:
            assert post.title in f.read()

    def test_outputs_post_files(self, tmpdir, post, template_dir):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'posts')
        presenter = presenters.HTMLPresenter(template_dir)

        presenter.output([post], target_dir)

        assert target_dir.exists()
        post_files = [f for f in target_dir.iterdir() if f.is_file()]
        assert len(post_files) == 1
        assert post_files[0].name == post.title.lower() + '.html'

        with open(post_files[0], 'r') as f:
            contents = f.read()
            assert post.title in contents
            assert post.date in contents
            assert post.contents in contents

    def test_outputs_multiple_files(self, tmpdir, post, template_dir):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'posts')
        presenter = presenters.HTMLPresenter(template_dir)
        post2 = post._replace(
            title='Second post', standardized_name='second-post')
        post3 = post._replace(
            title='Third post', standardized_name='third-post')
        posts = [post, post2, post3]

        presenter.output(posts, target_dir)

        assert target_dir.exists()
        post_files = [f for f in target_dir.iterdir() if f.is_file()]
        assert len(post_files) == 3
        # too many asserts?
        for idx, p_file in enumerate(sorted(post_files)):
            assert p_file.name == posts[idx].standardized_name + '.html'
            with open(p_file, 'r') as f:
                assert posts[idx].title in f.read()
