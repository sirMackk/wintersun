import pytest

from wintersun import post_reader


@pytest.fixture
def dict_contents():
    return {
        'title': 'Test Post',
        'date': '2014-12-31 01:16:13',
        'template': 'Post',
        'tags': ['tag1', 'tag2'],
        'contents': ('<p>Lorem ipsum dolor sit amet, consectetur adipiscing '
                     'elit. Praesent ultrices sit amet purus nec sollicitudin.'
                     'Donec vitae ipsum vel sapien molestie laoreet ac sed leo.'
                     'Vestibulum eget enim tempor, dictum nisl eu, tempus quam.'
                     'Aliquam fringilla elit non nunc condimentum, vitae '
                     'luctus quam facilisis.</p>\n')}


@pytest.fixture
def md_contents(dict_contents):
    title = dict_contents['title']
    date = dict_contents['date']
    template = dict_contents['template']
    tags = ' '.join(dict_contents['tags'])
    contents = dict_contents['contents']
    contents = contents.replace('<p>', '').replace('</p>', '')
    return (f'Title: {title}\n'
            f'Date: {date}\n'
            f'Template: {template}\n'
            f'Tags: {tags}\n'
            '\n'
            f'{contents}\n')


class TestMdFileReader:
    def test_find_lists_all_files(self, tmpdir):
        posts = tmpdir.mkdir('posts')
        guides = tmpdir.mkdir('guides')
        p1 = posts.join('post1.md')
        p2 = posts.join('post2.md')
        p1.write('post1')
        p2.write('post1')
        g1 = guides.join('guide1.md')
        g1.write('guide1')

        file_paths = post_reader.MdFileReader.find(tmpdir.strpath)

        assert len(file_paths) == 3
        for path in file_paths:
            assert path.is_file()
        file_names = sorted([f.name for f in file_paths])
        assert file_names == ['guide1.md', 'post1.md', 'post2.md']
        parent_paths = sorted([f.parent.name for f in file_paths])
        assert parent_paths == ['guides', 'posts', 'posts']

    @pytest.mark.integration
    def test_read_from_root_returns_posts(self, tmpdir, md_contents,
                                          dict_contents):
        posts = tmpdir.mkdir('posts')
        p1 = posts.join('post1.md')
        p1.write(md_contents)
        md_contents = md_contents.replace('Test Post', 'Test Post 2')
        md_contents = md_contents.replace('2014-12-31', '2015-01-31')

        p2 = posts.join('post2.md')
        p2.write(md_contents)

        post1, post2 = post_reader.MdFileReader.read_from_root(tmpdir.strpath)

        assert post1 == dict_contents

    # add unit test that uses a mock that tests correct attributes
