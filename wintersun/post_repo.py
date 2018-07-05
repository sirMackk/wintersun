
import re
from collections import namedtuple

PostItem = namedtuple('PostItem', 'title, contents, template, date, tags')


# inherit from wintersunexc
class PostRepoException(Exception):
    pass


class NotFound(PostRepoException):
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
        pass

    def insert(self, title, contents, template, date=None, tags=None):
        self.posts.append(
            PostItem(title, contents, template, date, tags))

    def insert_from_file(self, fpath):
        pass

    def read_from_path(self, root):
        pass


class MdFileFinder:
    MARKDOWN_FILTER = re.compile(r'([a-zA-Z0-9_-]+)\.md')

    @staticmethod
    def find(root):
        pass
