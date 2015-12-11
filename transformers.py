import markdown


class CachingTransformer(object):
    cache = {}

    def __init__(self, transformer_cls):
        self.transformer = transformer_cls

    def _convert(self, file_like):
        with self.transformer() as tr:
            return tr.convert(file_like)

    def get_or_create(self, path, filename):
        key = filename
        if key in self.cache:
            return self.cache[key]
        else:
            with open(filename) as f:
                contents, meta = self._convert(unicode(f.read(), 'utf-8'))
                meta['filename'], meta['path'] = filename, path
                self.cache[key] = (contents, meta,)
                return contents, meta


class MarkdownTransformer(object):
    def __init__(self):
        self.md = markdown.Markdown(extensions=['markdown.extensions.meta'])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.md.reset()
        return False

    def convert(self, *args, **kwargs):
        converted = self.md.convert(*args, **kwargs)
        meta = {k: v[0] for k, v in self.md.Meta.iteritems()}
        return converted, meta
