from pathlib import Path

import markdown2


class MdFileReader:
    MD_GLOB = '**/*.md'

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
                'contents': str(html)})
        return md_posts

    @classmethod
    def _find(cls, root):
        root = Path(root)
        return list(root.glob(cls.MD_GLOB))
