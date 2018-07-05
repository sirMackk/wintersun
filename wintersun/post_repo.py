import re
from collections import namedtuple
from datetime import datetime

PostItem = namedtuple('PostItem', 'title, contents, template, date, tags')


# inherit from wintersunexc
class PostRepoException(Exception):
    pass


class NotFound(PostRepoException):
    pass


class DuplicatePost(PostRepoException):
    pass


class InMemPostRepo:
    def __init__(self):
        self.posts = []

    def get(self, title):
        for post in self.posts:
            if post.title == title:
                return post
        raise NotFound(f'Post "{title}" not found')

    def all(self, order='desc'):
        if order not in ('asc', 'desc'):
            raise PostRepoException(f'Invalid sorting order: "{order}"')
        reverse = order == 'desc'
        ordered_posts = sorted(
            self.posts,
            key=lambda post: self._to_dt(post.date),
            reverse=reverse)
        return ordered_posts

    def insert(self, title, contents, template, date=None, tags=None):
        try:
            existing = self.get(title)
            raise DuplicatePost(
                f'Post titled "{title}" from "{existing.date}" already exists, '
                f'cannot insert post dated "{date}"')
        except NotFound:
            self.posts.append(
                PostItem(title, contents, template, date, tags))

    def _to_dt(self, dt_str):
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

    def __len__(self):
        return len(self.posts)


class MdFileFinder:
    MARKDOWN_FILTER = re.compile(r'([a-zA-Z0-9_-]+)\.md')

    @staticmethod
    def find(root):
        pass
