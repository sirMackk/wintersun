from pathlib import Path

import pytest

from wintersun import exceptions, post_item, presenters


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
    return post_item.PostItem('Post-Title', 'Lorem ipsum', 'post-title',
                              'Post', '2018-01-01', ['programming'])


@pytest.fixture
def mock_renderer(mocker):
    def _echo(*args, **kwargs):
        return f'{args} - {kwargs}'
    renderer = mocker.Mock()
    renderer.render.side_effect = _echo
    return renderer


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
    def test_outputs_index_file(self, tmpdir, post, mock_renderer):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'posts')
        presenter = presenters.HTMLPresenter(mock_renderer)

        presenter.output([post], target_dir)

        index_fpath = target_dir.absolute().parent / 'posts.html'
        assert index_fpath.exists()
        with open(index_fpath, 'r') as f:
            assert post.title in f.read()

    def test_outputs_post_files(self, tmpdir, post, mock_renderer):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'posts')
        presenter = presenters.HTMLPresenter(mock_renderer)

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

    def test_outputs_multiple_files(self, tmpdir, post, mock_renderer):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'posts')
        presenter = presenters.HTMLPresenter(mock_renderer)
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


class TestTagPresenter:
    def test_generate_one_index_with_posts(self, tmpdir, mock_renderer, post):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'tags')
        presenter = presenters.TagPresenter(mock_renderer)

        presenter.output([post], target_dir)

        assert target_dir.exists()
        index_files = [f for f in target_dir.iterdir() if f.is_file()]
        expected_index_file = post.tags[0] + '.html'
        assert index_files[0].parent.name == 'tags'
        assert index_files[0].name == expected_index_file

        with open(index_files[0], 'r') as f:
            assert post.title in f.read()

    def test_generate_multiple_indexes(self, tmpdir, mock_renderer, post):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'tags')
        presenter = presenters.TagPresenter(mock_renderer)
        post2 = post._replace(tags=['linux'], title='linux post')

        presenter.output([post, post2], target_dir)

        index_files = sorted([f for f in target_dir.iterdir() if f.is_file()])
        assert len(index_files) == 2
        assert index_files[0].name == 'linux.html'
        assert index_files[1].name == 'programming.html'

        with open(index_files[0], 'r') as f:
            assert post2.title in f.read()

        with open(index_files[1], 'r') as f:
            assert post.title in f.read()

    def test_generate_overlapping_indexes(self, tmpdir, mock_renderer, post):
        container_dir = tmpdir.mkdir('test')
        target_dir = Path(container_dir, 'tags')
        presenter = presenters.TagPresenter(mock_renderer)
        post2 = post._replace(
            tags=['linux', 'programming'], title='linux programming post')

        presenter.output([post, post2], target_dir)
        index_files = sorted([f for f in target_dir.iterdir() if f.is_file()])
        assert len(index_files) == 2

        # index_files[1] == programming.html
        with open(index_files[1], 'r') as f:
            contents = f.read()
            assert post.title in contents
            assert post2.title in contents

        with open(index_files[0], 'r') as f:
            assert post2.title in f.read()

    def test_untagged_page_raises_error(self, tmpdir, mock_renderer, post):
        post2 = post._replace(tags=[])
        target_dir = Path(tmpdir.strpath, 'test')
        presenter = presenters.TagPresenter(mock_renderer)
        with pytest.raises(exceptions.IncompletePage):
            presenter.output([post2], target_dir)
