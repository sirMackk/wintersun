import markdown


class MarkdownTransformer(object):
    def __init__(self):
        self.md = markdown.Markdown(extensions=['markdown.extensions.meta'])
        self.Meta = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.md.reset()
        return False

    def convert(self, *args, **kwargs):
        converted = self.md.convert(*args, **kwargs)
        self.Meta.update({k: v[0] for k, v in self.md.Meta.iteritems()})
        return converted

    def convert_utf8(self, f):
        return self.convert(unicode(f.read(), 'utf-8'))
