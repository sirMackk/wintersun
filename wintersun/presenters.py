from datetime import datetime
from pathlib import Path

import pytz

from atom_generator import Feed


class AtomPresenter:
    def __init__(self, config):
        self.config = config

    def output(self, posts, target='./feed'):
        target_path = Path(target)
        # maybe this dict should be offloaded to the Feed object?
        feed = Feed([
            {'name': 'title',
             'value': self.config['feed_title']},
            {'name': 'link',
                'attributes': {
                    'rel': 'self',
                    'href': self.config['site_url'] + '/'}},
            {'name': 'link',
                'attributes': {
                    'rel': 'alternate',
                    'href': self.config['site_url']}},
            {'name': 'id',
                'value': self.config['site_url'] + '/'},
            {'name': 'updated',
                'value': self._create_timestamp()}])
        with open(target_path, 'w', encoding=self.config['encoding']) as f:
            for post in posts:
                if self._is_template('post', post):
                    feed.add_entry(
                        self._generate_atom_entry_dict(post))
            f.write(feed.generate_xml())

    def _is_template(self, template_type, post):
        # is this required at all?
        return post.template == template_type.capitalize()

    def _create_timestamp(self, date=None):
        # rfc3339 timestamp
        # is this important?
        if date:
            return date + 'T00:00:00+01:00'
        else:
            localtz = pytz.timezone("America/New_York")
            return datetime.now().replace(tzinfo=localtz).strftime(
                "%Y-%m-%dT%H:%M:%S+01:00")

    def _generate_entry_link(self, post):
        # too much dependency on config?
        # extract stuff like site_url and post_dir into object ins. args?
        return '/'.join([
            self.config['site_url'],
            self.config['post_dir'],
            post.standardized_name + '.html'])

    def _generate_atom_entry_dict(self, post):
        entry = {
            'title': post.title,
            'link': self._generate_entry_link(post),
            'published': self._create_timestamp(post.date),
            'updated': self._create_timestamp(post.date),
            'name': self.config['author'],
            'content': post.contents[:100] + '...'}
        return entry
