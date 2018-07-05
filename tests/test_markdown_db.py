import pytest

from wintersun import markdown_db


@pytest.fixture
def example_post_dict():
    return {
        'title': 'Test Post',
        'contents': 'A bunch of contents\nMany pages',
        'date': '2014-12-31 01:16:13',
        'tags': ['python', 'software']
    }


@pytest.fixture
def md_post_db():
    return markdown_db.MdPostDb()


class TestMdPostDb:
    def test_insert_adds_postitem(self, example_post_dict, md_post_db):
        md_post_db.insert(**example_post_dict)
        expected_post = markdown_db.PostItem(**example_post_dict)

        assert len(md_post_db.posts) == 1
        md_post_db.posts[0] == expected_post

    def test_get_retrieves_post_by_title(self, example_post_dict, md_post_db):
        md_post_db.insert(**example_post_dict)
        post = md_post_db.get(example_post_dict['title'])

        post_dict = post._asdict()
        assert post_dict == example_post_dict

    def test_get_inexistent_post_raises_notfound(self, md_post_db):
        title = 'some random title'
        with pytest.raises(markdown_db.NotFound) as exc:
            md_post_db.get(title)

            assert title in str(exc.value)
