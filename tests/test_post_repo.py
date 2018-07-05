import pytest

from wintersun import post_repo


@pytest.fixture
def example_post_dict():
    return {
        'title': 'Test Post',
        'template': 'Post',
        'contents': 'A bunch of contents\nMany pages',
        'date': '2014-12-31 01:16:13',
        'tags': ['python', 'software']
    }


@pytest.fixture
def inmem_repo():
    return post_repo.InMemPostRepo()


class TestMdPostDb:
    def test_insert_adds_postitem(self, example_post_dict, inmem_repo):
        inmem_repo.insert(**example_post_dict)
        expected_post = post_repo.PostItem(**example_post_dict)

        assert len(inmem_repo.posts) == 1
        inmem_repo.posts[0] == expected_post

    def test_get_retrieves_post_by_title(self, example_post_dict, inmem_repo):
        inmem_repo.insert(**example_post_dict)
        post = inmem_repo.get(example_post_dict['title'])

        post_dict = post._asdict()
        assert post_dict == example_post_dict

    def test_get_inexistent_post_raises_notfound(self, inmem_repo):
        title = 'some random title'
        with pytest.raises(post_repo.NotFound) as exc:
            inmem_repo.get(title)

            assert title in str(exc.value)
