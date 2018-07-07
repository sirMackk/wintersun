import pytest

from wintersun import post_reader


@pytest.fixture
def dict_contents():
    return {
        'title': 'Test Post',
        'date': '2014-12-31 01:16:13',
        'template': 'Post',
        'standardized_name': 'post1-about---things',
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
    @pytest.mark.integration
    def test_read_from_root_returns_posts(self, tmpdir, md_contents,
                                          dict_contents):
        posts = tmpdir.mkdir('posts')
        p1 = posts.join('post1_about_@_things.md')
        p1.write(md_contents)
        md_contents = md_contents.replace('Test Post', 'Test Post 2')
        md_contents = md_contents.replace('2014-12-31', '2015-01-31')

        p2 = posts.join('post2.md')
        p2.write(md_contents)

        posts = post_reader.MdFileReader.read(tmpdir.strpath)
        if posts[0]['title'] == 'Test Post':
            post = posts[0]
        else:
            post = posts[1]

        assert post == dict_contents
