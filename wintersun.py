import markdown
import os.path as os_path
import os
import re
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader

MARKDOWN_FILTER = re.compile(r'([a-zA-Z0-9_-]+)\.md')
TEMPLATED_FILENAME_FILTER = re.compile(r'[^a-z^A-Z^0-9-]')

TEMPLATE_DIR = 'templates'
TARGET_DIR = './site'

EXCLUDED_DIRS = ['tags', TEMPLATE_DIR, 'media', 'static', 'tests', TARGET_DIR]
# use imagemagick to process media into thumbnails
# gulp for css + js
# use threading/multiprocessing for recursion? any global state?


# put into if name = main
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def get_items_from_path(path, fn=os_path.isfile):
    for filename in os.listdir(path):
        full_path = os_path.join(path, filename)
        if fn(full_path):
            yield full_path


def get_markdown_files(filenames):
    for filename in filenames:
        if MARKDOWN_FILTER.match(filename):
            yield filename


def build_tags(path):
    # process files looking at Meta for tags
    # create list of namedtuples with title: tag
    # use this to create index of titles for each tag
    pass


def build_index(path, title):
    directory_name = MARKDOWN_FILTER.match(title).groups()

    if not directory_name:
        return []

    directory_name = directory_name.groups()[0]
    directory_path = os_path.join(path, directory_name)

    # process files using markdown to extract title + date, sort by date
    return (file_name for file_name in os.listdir(directory_path)
            if os_path.isfile(directory_path + file_name) and
            MARKDOWN_FILTER.match(file_name)), directory_path


def templated_content(path, contents, meta):
    template = env.get_template(meta.template.lower() + '.html')
    if meta.template == 'Index':
        meta['indexed'], meta['indexed_dir'] = build_index(path, meta['title'])

    return template.render(
        path=path,
        contents=contents,
        meta=meta)


def build_tree(path):
    directories = get_items_from_path(path, fn=os_path.isdir)
    md_files = get_markdown_files(get_items_from_path(path, fn=os_path.isfile))

    md = markdown.Markdown(extensions=['markdown.extensions.meta'])

    # possible to use map/threads here
    # map filenames into Queue?
    for md_file in md_files:
        with open(md_file, 'r') as f:
            marked_up = md.convert(f.read())
            templated_item = templated_content(path, marked_up, md.Meta)
            md.reset()

            output_file = os_path.join(
                TARGET_DIR,
                path,
                TEMPLATED_FILENAME_FILTER.sub(md_file, '-') + '.html')

            with open(output_file, 'wb') as out:
                out.write(templated_item)

    for directory in directories:
        if directory not in EXCLUDED_DIRS:
            print 'making dir: {}'.format(directory)
            os.mkdir(TARGET_DIR + path + directory, 0755)
            build_tree(path + directory)
