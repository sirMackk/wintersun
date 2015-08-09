import markdown
import os.path as os_path
from sys import exit
import os
from shutil import rmtree, copytree
import re
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader, PackageLoader

from atom_generator import Feed, create_timestamp

# what if these lived in a config namedtuple?
MARKDOWN_FILTER = re.compile(r'([a-zA-Z0-9_-]+)\.md')
TEMPLATED_FILENAME_FILTER = re.compile(r'[^a-z^A-Z^0-9-]')
REMOVE_LEADING_SLASHES = re.compile(r'^[a-zA-Z0-9\.\/]*\/')
REMOVE_RELATIVE_SLASHES = re.compile(r'\./')
REMOVE_TRAILING_SUFFIX = re.compile(r'\.md$')
SITE_URL = 'http://mattscodecave.com'

TEMPLATE_DIR = './wintersun/templates'
STATIC_DIR = './wintersun/static'
TARGET_DIR = './site'

EXCLUDED_DIRS = ['./tags', TEMPLATE_DIR, './media', STATIC_DIR, './tests',
                 TARGET_DIR, './wintersun']

FEED = Feed([
    {'name': 'title',
     'value': 'mattscodecave.com'},
    {'name': 'link',
        'attributes': {
            'rel': 'self',
            'href': SITE_URL + '/'}},
    {'name': 'link',
        'attributes': {
            'rel': 'alternate',
            'href': SITE_URL}},
    {'name': 'id',
        'value': SITE_URL + '/'},
    {'name': 'updated',
        'value': create_timestamp()}])

env = Environment(loader=PackageLoader('wintersun'))


def get_items_from_path(path, fn=os_path.isfile):
    for filename in os.listdir(path):
        full_path = os_path.join(path, filename)
        if fn(full_path):
            yield full_path


def get_markdown_files(filenames):
    for filename in filenames:
        if MARKDOWN_FILTER.search(filename):
            yield filename


def standardize_filename(filename):
    return TEMPLATED_FILENAME_FILTER.sub(
        '-',
        REMOVE_TRAILING_SUFFIX.sub(
            '',
            REMOVE_LEADING_SLASHES.sub('', filename)))


def build_tags(path):
    # process files looking at Meta for tags
    # create list of namedtuples with title: tag
    # use this to create index of titles for each tag
    pass


def build_index(path, filename):
    directory_name = MARKDOWN_FILTER.search(filename).groups()

    if not directory_name:
        return []

    directory_name = directory_name[0]
    directory_path = os_path.join(path, directory_name)

    # process files using markdown to extract title + date, sort by date
    return (standardize_filename(file_name) for file_name
            in os.listdir(directory_path)
            if os_path.isfile(os_path.join(directory_path, file_name)) and
            MARKDOWN_FILTER.match(file_name)), directory_path


def templated_content(filename, path, contents, meta):
    template = env.get_template(meta['template'][0].lower() + '.html')
    # debugging
    print u'template meta title: {}'.format(meta['title'][0])
    if meta['template'][0] in ('Index', 'Main',):
        meta['indexed'], meta['indexed_dir'] = build_index(path, filename)

    return template.render(
        path=path,
        contents=contents,
        meta=meta)


def generate_entry_link(md_file, path):
    return '/'.join(
        [SITE_URL,
         REMOVE_RELATIVE_SLASHES.sub('', path),
         standardize_filename(md_file) + '.html'])


def generate_atom_entry(contents, md_file, path, meta):
    entry = {
        u'title': meta['title'][0],
        u'link': generate_entry_link(md_file, path),
        u'published': create_timestamp(meta['date'][0]),
        u'updated': create_timestamp(meta['date'][0]),
        u'name': u'Matt',
        u'content': contents[:100] + '...'}

    return entry


def build_tree(path):
    directories = get_items_from_path(path, fn=os_path.isdir)
    md_files = get_markdown_files(get_items_from_path(path, fn=os_path.isfile))

    md = markdown.Markdown(extensions=['markdown.extensions.meta'])

    for md_file in md_files:
        print u'md_file: {}'.format(md_file)
        with open(md_file) as f:
            marked_up = md.convert(unicode(f.read(), 'utf-8'))
            templated_item = templated_content(md_file, path,
                                               marked_up, md.Meta)
            if u'Post' in md.Meta['template']:
                FEED.add_entry(generate_atom_entry(
                    marked_up, md_file, path, md.Meta))
            md.reset()

            print u'creating file: {}'.format(
                standardize_filename(md_file.strip()) + '.html')

            output_file = os_path.join(
                TARGET_DIR,
                path,
                standardize_filename(md_file) + '.html')

            with open(output_file, mode='w') as out:
                out.write(templated_item.encode('utf-8-sig'))

    for directory in directories:
        if directory not in EXCLUDED_DIRS:
            print u'making dir: {}'.format(directory)
            os.mkdir(os_path.join(TARGET_DIR, path, directory), 0755)
            build_tree(os_path.join(path, directory))



def prepare_target_dir():
    def setup_target_dir():
        os.mkdir(TARGET_DIR, 0755)
        copytree(STATIC_DIR, os_path.join(TARGET_DIR, './static'))

    if not os_path.exists(TARGET_DIR):
        setup_target_dir()
        return

    if os_path.isdir(TARGET_DIR):
        if raw_input("{} exists! Enter y to delete and continue: ".format(
                     TARGET_DIR)).lower() == 'y':
            rmtree(TARGET_DIR)
            setup_target_dir()
        else:
            exit()


if __name__ == '__main__':
    prepare_target_dir()
    build_tree('./')

    with open(os_path.join(TARGET_DIR, 'feed'), 'wb') as f:
        f.write(FEED.generate_xml())
