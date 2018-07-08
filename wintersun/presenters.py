from datetime import datetime
from pathlib import Path

import pytz

from atom_generator import Feed


class AtomPresenter:
    def __init__(self, feed_title, site_url, post_dir, author, encoding):
        self.feed_title = feed_title
        self.site_url = site_url
        self.post_dir = post_dir
        self.author = author
        self.encoding = encoding

    def output(self, posts, target='./feed'):
        target_path = Path(target)
        feed = Feed(self.feed_title, self.site_url,
                    self._create_timestamp())
        with open(target_path, 'w', encoding=self.encoding) as f:
            for post in posts:
                if post.template == 'Post':
                    feed.add_entry(
                        self._generate_atom_entry_dict(post))
            f.write(feed.generate_xml())

    def _create_timestamp(self, date=None):
        if date:
            return date + 'T00:00:00+01:00'
        else:
            localtz = pytz.timezone("America/New_York")
            return datetime.now().replace(tzinfo=localtz).strftime(
                "%Y-%m-%dT%H:%M:%S+01:00")

    def _generate_entry_link(self, post):
        return '/'.join(
            [self.site_url, self.post_dir, post.standardized_name + '.html'])

    def _generate_atom_entry_dict(self, post):
        entry = {
            'title': post.title,
            'link': self._generate_entry_link(post),
            'published': self._create_timestamp(post.date),
            'updated': self._create_timestamp(post.date),
            'name': self.author,
            'content': post.contents[:100] + '...'}
        return entry
