import itertools
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pytz

from wintersun import atom_generator, exceptions


class AtomPresenter:
    def __init__(self, feed_title, site_url, post_dir, author, encoding):
        self.feed_title = feed_title
        self.site_url = site_url
        self.post_dir = post_dir
        self.author = author
        self.encoding = encoding

    def output(self, posts, target='./feed'):
        """
        :param posts: List of PostItem-like objects.
        :param target: Target Atom feed file path.
        """
        target_path = Path(target)
        feed = atom_generator.Feed(self.feed_title, self.site_url,
                                   self._rfc3339_ts_now())
        with open(target_path, 'w', encoding=self.encoding) as f:
            for post in posts:
                if post.template in ('Post', 'Essay'):
                    feed.add_entry(
                        self._generate_atom_entry_dict(post))
            f.write(feed.generate_xml())

    def _rfc3339_suffix(self, date):
        return date + 'T00:00:00-05:00'

    def _rfc3339_ts_now(self):
        localtz = pytz.timezone("America/New_York")
        return datetime.now().replace(tzinfo=localtz).strftime(
            "%Y-%m-%dT%H:%M:%S-05:00")

    def _generate_entry_link(self, post):
        return '/'.join(
            [self.site_url, self.post_dir, post.standardized_name + '.html'])

    def _generate_atom_entry_dict(self, post):
        entry = {
            'title': post.title,
            'link': self._generate_entry_link(post),
            'published': self._rfc3339_suffix(post.date),
            'updated': self._rfc3339_suffix(post.date),
            'name': self.author,
            'content': post.contents[:100] + '...'}
        return entry


class HTMLIndexPresenter:
    """Generate index HTML files for posts."""
    def __init__(self, html_renderer, site_url, post_dir):
        self.renderer = html_renderer
        self.site_url = site_url
        self.post_dir = post_dir

    def output(self, posts, template_name, target_dir, grouped=True):
        # 'grouped' is confusing, because the template should imply it
        # ugly pluralization + suffix; Document naming convention.
        index_tpl_name = template_name + 's_index.html'
        target_fpath = target_dir / (template_name + 's.html')
        index_entries = self._generate_index_entries(posts)
        if grouped:
            index_entries = {
                k: list(group)
                for k, group in self._group_by_year(index_entries)
            }

        with open(target_fpath, 'w') as f:
            f.write(self.renderer.render(index_tpl_name, entries=index_entries))

    def _generate_index_entries(self, posts):
        entries = [{
            'title': post.title,
            'date': post.date,
            'link': self._generate_entry_link(post)
        } for post in posts]
        return entries

    def _group_by_year(self, entries):
        def _key(item):
            # eg. item['date'] == '2018-01-01'
            return item['date'].split('-')[0]

        return itertools.groupby(entries, _key)

    # duplicate code, think about extracting into own object eg. LinkGenerator
    def _generate_entry_link(self, post):
        return '/'.join(
            [self.site_url, self.post_dir, post.standardized_name + '.html'])


class HTMLPresenter:
    """Convert existing contents into HTML files."""
    def __init__(self, html_renderer):
        self.renderer = html_renderer

    def output(self, posts, target_dir):
        self._write_posts(posts, target_dir)

    def _write_posts(self, posts, target_dir):
        target_dir.mkdir(mode=0o755, exist_ok=True)
        for post in posts:
            template_name = post.template.lower() + '.html'
            post_fpath = target_dir / (post.standardized_name + '.html')
            with open(post_fpath, 'w') as f:
                f.write(self.renderer.render(template_name, post=post))


class TagPresenter:
    def __init__(self, html_renderer, site_url, post_dir):
        self.renderer = html_renderer
        self.site_url = site_url
        self.post_dir = post_dir

    def _extract_by_tag(self, posts):
        tagged_posts = defaultdict(list)
        for post in posts:
            if len(post.tags) == 0:
                raise exceptions.IncompletePost(
                    f'post {post} missing "tags"')
            for tag in post.tags:
                tagged_posts[tag].append({
                    'title': post.title,
                    'date': post.date,
                    'link': self._generate_entry_link(post)
                })
        return tagged_posts

    def _generate_entry_link(self, post):
        return '/'.join(
            [self.site_url, self.post_dir, post.standardized_name + '.html'])

    def output(self, posts, target_dir):
        target_dir.mkdir(mode=0o755)
        tagged_posts = self._extract_by_tag(posts)

        for tag, post_list in tagged_posts.items():
            index_fpath = target_dir / (tag + '.html')
            with open(index_fpath, 'w') as f:
                f.write(
                    self.renderer.render(
                        'tag.html', tag=tag, tagged_items=post_list))
