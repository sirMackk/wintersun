import re
from pathlib import Path

import markdown2


class MdFileReader:
    MD_GLOB = '**/*.md'
    TEMPLATED_FILENAME_FILTER = re.compile(r'[^a-z^A-Z^0-9-]')

    @classmethod
    def read(cls, root):
        return cls._read_from_root(root)

    @classmethod
    def _read_from_root(cls, root):
        md_files = cls._find(root)
        md_posts = []
        for md_file_path in md_files:
            html = markdown2.markdown_path(md_file_path, extras=['metadata'])
            md_posts.append({
                'title': html.metadata['Title'],
                'date': html.metadata['Date'],
                'template': html.metadata['Template'],
                'tags': html.metadata['Tags'].split(' '),
                'standardized_name': cls._standardize_filename(md_file_path),
                'contents': str(html)})
        return md_posts

    @classmethod
    def _find(cls, root):
        root = Path(root)
        return list(root.glob(cls.MD_GLOB))

    @classmethod
    def _standardize_filename(cls, filename):
        return cls.TEMPLATED_FILENAME_FILTER.sub('-', filename.stem)
