from datetime import datetime

from wintersun import exceptions, post_item


class InMemPostRepo:
    def __init__(self):
        self.posts = []

    def get(self, title):
        for post in self.posts:
            if post.title == title:
                return post
        raise exceptions.NotFound(f'Post "{title}" not found')

    def all(self, order='desc'):
        if order not in ('asc', 'desc'):
            raise exceptions.PostRepoException(
                f'Invalid sorting order: "{order}"')
        reverse = order == 'desc'
        ordered_posts = sorted(
            self.posts,
            key=lambda post: self._to_dt(post.date),
            reverse=reverse)
        return ordered_posts

    def insert(self,
               title,
               contents,
               standardized_name,
               template,
               date,
               tags=None):
        tags = tags if tags else []
        try:
            existing = self.get(title)
            raise exceptions.DuplicatePost(
                f'Post titled "{title}" from "{existing.date}" already exists, '
                f'cannot insert post dated "{date}"')
        except exceptions.NotFound:
            self.posts.append(
                post_item.PostItem(title, contents, standardized_name,
                                   template, date, tags))

    def _to_dt(self, dt_str):
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

    def __len__(self):
        return len(self.posts)
