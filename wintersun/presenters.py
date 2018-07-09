from datetime import datetime
from pathlib import Path

import pytz

from wintersun import atom_generator


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
                if post.template == 'Post':
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


class HTMLPresenter:
    def __init__(self, html_renderer):
        self.renderer = html_renderer

    def output(self, pages, target_dir):
        self._write_index(pages, target_dir)
        self._write_pages(pages, target_dir)

    def _write_index(self, pages, target_dir):
        # different indexes for different page categories?
        index_fpath = target_dir.absolute().parent / (target_dir.stem + '.html')
        with open(index_fpath, 'w') as f:
            f.write(self.renderer.render('index.html', pages=pages))

    def _write_pages(self, pages, target_dir):
        target_dir.mkdir(mode=0o755)
        for page in pages:
            template_name = page.template.lower() + '.html'
            page_fpath = target_dir / (page.standardized_name + '.html')
            page_contents = {
                'title': page.title,
                'date': page.date,
                'contents': page.contents
            }
            with open(page_fpath, 'w') as f:
                f.write(self.renderer.render(template_name, **page_contents))
