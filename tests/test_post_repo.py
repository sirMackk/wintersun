import pytest

from wintersun import exceptions, post_item, post_repo


@pytest.fixture
def example_post_dict():
    return {
        'title': 'Test Post',
        'template': 'Post',
        'standardized_name': 'test-post',
        'contents': 'A bunch of contents\nMany Posts',
        'date': '2014-12-31 01:16:13',
        'tags': ['python', 'software']
    }


@pytest.fixture
def inmem_repo(example_post_dict):
    repo = post_repo.InMemPostRepo()
    repo.insert(**example_post_dict)
    return repo


class TestInMemPostRepo:
    def test_insert_adds_postitem(self, example_post_dict, inmem_repo):
        expected_post = post_item.PostItem(**example_post_dict)

        assert len(inmem_repo.posts) == 1
        inmem_repo.posts[0] == expected_post

    def test_insert_duplicate_post_raises(self, inmem_repo, example_post_dict):
        first_date = example_post_dict['date']
        example_post_dict['date'] = '2017-12-31 06:00:00'
        with pytest.raises(exceptions.DuplicatePost) as exc:
            inmem_repo.insert(**example_post_dict)

        exc_msg = str(exc)
        assert example_post_dict['title'] in exc_msg
        assert first_date in exc_msg
        assert example_post_dict['date'] in exc_msg

    def test_get_retrieves_post_by_title(self, example_post_dict, inmem_repo):
        post = inmem_repo.get(example_post_dict['title'])

        post_dict = post._asdict()
        assert post_dict == example_post_dict

    def test_get_inexistent_post_raises_notfound(self, inmem_repo):
        title = 'some random title'
        with pytest.raises(exceptions.NotFound) as exc:
            inmem_repo.get(title)

            assert title in str(exc.value)

    def test_all_gets_all_posts(self, inmem_repo, example_post_dict):
        first_title = example_post_dict['title']
        example_post_dict['title'] = 'Second post'
        inmem_repo.insert(**example_post_dict)
        posts = inmem_repo.all()
        assert len(inmem_repo) == 2
        titles = [post.title for post in posts]
        assert titles == [first_title, example_post_dict['title']]

    def test_all_returns_sorted_posts(self, inmem_repo, example_post_dict):
        first_title = example_post_dict['title']
        second_post = example_post_dict
        second_post['title'] = 'Second title'
        second_post['date'] = '2015-01-01 01:16:13'
        inmem_repo.insert(**second_post)

        desc_posts = inmem_repo.all(order='desc')
        asc_posts = inmem_repo.all(order='asc')

        desc_titles = [post.title for post in desc_posts]
        asc_titles = [post.title for post in asc_posts]

        assert desc_titles == [second_post['title'], first_title]
        assert asc_titles == [first_title, second_post['title']]

    def test_all_invalid_sorting_order_raises(self, inmem_repo):
        with pytest.raises(exceptions.PostRepoException) as exc:
            inmem_repo.all(order='wat')

            assert 'Invalid sorting order' in str(exc)

    def test_get_items_by_template(self, inmem_repo, example_post_dict):
        first_post = example_post_dict
        second_post = first_post.copy()
        second_post['title'] = 'Second Essay'
        second_post['template'] = 'Essay'
        inmem_repo.insert(**second_post)

        posts = inmem_repo.all_by_template('Post')
        essays = inmem_repo.all_by_template('Essay')

        assert len(posts) == 1
        assert len(essays) == 1

        assert posts[0].title == example_post_dict['title']
        assert essays[0].title == second_post['title']
