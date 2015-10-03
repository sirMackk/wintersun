import argparse
import os.path as os_path
from sys import exit, stdout
import os
from shutil import rmtree, copytree
import re
from collections import namedtuple
import logging

import markdown
from jinja2 import Environment, PackageLoader
from datetime import datetime

from atom_generator import Feed, create_timestamp

ARGS = None

MARKDOWN_FILTER = re.compile(r'([a-zA-Z0-9_-]+)\.md')
TEMPLATED_FILENAME_FILTER = re.compile(r'[^a-z^A-Z^0-9-]')
LEADING_SLASHES = re.compile(r'^[a-zA-Z0-9\.\/]*\/')
RELATIVE_SLASHES = re.compile(r'\./')
TRAILING_SUFFIX = re.compile(r'\.md$')

SITE_URL = 'http://mattscodecave.com'
TEMPLATE_DIR = './wintersun/templates'
STATIC_DIR = './wintersun/static'
TARGET_DIR = './site'
OUTPUT_ENCODING = 'utf-8-sig'

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
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stdout))
logger.setLevel(logging.INFO)


class MarkdownTransformer(object):
    def __init__(self):
        self.md = markdown.Markdown(extensions=['markdown.extensions.meta'])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.md.reset()
        return False

    def convert(self, *args, **kwargs):
        return self.md.convert(*args, **kwargs)

    def convert_utf8(self, f):
        return self.convert(unicode(f.read(), 'utf-8'))

    @property
    def Meta(self):
        return self._meta()

    def _meta(self):
        return {k: v[0] for k, v in self.md.Meta.iteritems()}


def build_tree(path):
    directories, input_files = get_files_and_directories_from(path)

    for md_file in input_files:
        logger.info(u'input file: %s', md_file)
        transform_into_output(md_file, path)

    transform_next_dir_level(path, directories)


def get_files_and_directories_from(dir_path):
    directories = filter_items_from_path(dir_path, filter_fn=os_path.isdir)
    md_files = get_markdown_files(
        filter_items_from_path(dir_path, filter_fn=os_path.isfile))
    return directories, md_files


def transform_into_output(md_file, path):
    with MarkdownTransformer() as md:
        md.Meta['filename'], md.Meta['path'] = md_file, path
        transformed = apply_transformer(md)
        contents = apply_template(transformed, md.Meta)

        write_output_file(contents, md.Meta)


def apply_template(contents, meta):
    templated_item = render_template(contents, meta)
    if is_template('post', meta):
        update_feed(FEED, contents, meta)

    return templated_item


def apply_transformer(transformer):
    meta = transformer.Meta
    with open(meta['filename']) as f:
        return transformer.convert_utf8(f)


def is_template(template_type, meta):
    return meta['template'] == unicode(template_type).capitalize()


def render_template(contents, meta):
    logger.info(u'template meta title: %s', meta['title'])
    template = get_template(meta['title'])
    if is_template('index', meta) or is_template('main', meta):
        meta['indexed'], meta['indexed_dir'] = generate_post_index(meta)

    return template.render(
        contents=contents,
        meta=meta)


def get_template(title):
    return env.get_template(title.lower() + 'html')


def write_output_file(contents, meta):
    path = meta['path']
    out_filename = standardize_filename(meta['filename'].strip()) + '.html'

    logger.info(u'creating file: %s',
                out_filename)

    output_destination_path = os_path.join(
        TARGET_DIR,
        path,
        out_filename)

    with open(output_destination_path, mode='w') as out:
        out.write(contents.encode(OUTPUT_ENCODING))


def transform_next_dir_level(path, directories):
    # abstraction level mix - too many topics?
    for directory in directories:
        if directory not in EXCLUDED_DIRS:
            logger.info(u'making dir: %s', directory)
            os.mkdir(os_path.join(TARGET_DIR, path, directory), 0755)
            build_tree(os_path.join(path, directory))


def generate_post_index(meta):
    index_directory_name = MARKDOWN_FILTER.search(meta['filename']).groups()

    if not index_directory_name:
        return []

    index_directory_path = os_path.join(meta['path'], index_directory_name[0])
    return filenames_by_date(index_directory_path), index_directory_path


PostItem = namedtuple('PostItem', 'filename, title, date')


def create_postitem(file_name, file_meta):
    return PostItem._make((
        standardize_filename(file_name),
        file_meta['title'],
        convert_date_time(file_meta['date']),))


def filenames_by_date(dir_path):
    files = []
    _, input_files = get_files_and_directories_from(dir_path)

    with MarkdownTransformer() as md:
        for input_file in input_files:
            with open(input_file, 'rb') as f:
                md.convert_utf8(f)
                input_file_meta = md.Meta
                files.append(create_postitem(input_file, input_file_meta))

    return sorted(
        files,
        key=lambda post_item: post_item.date,
        reverse=True)


def generate_entry_link(md_file, path):
    return '/'.join(
        [SITE_URL,
         RELATIVE_SLASHES.sub('', path),
         standardize_filename(md_file) + '.html'])


def generate_atom_entry_dict(contents, meta):
    entry = {
        u'title': meta['title'],
        u'link': generate_entry_link(meta['filename'], meta['path']),
        u'published': create_timestamp(meta['date']),
        u'updated': create_timestamp(meta['date']),
        u'name': u'Matt',
        u'content': contents[:100] + '...'}

    return entry


def update_feed(feed, marked_up, md_meta):
    feed.add_entry(generate_atom_entry_dict(marked_up, md_meta))


def build_path(node, path):
    return os_path.join(path, node)


def filter_items_from_path(path, filter_fn=os_path.isfile):
    for item in os.listdir(path):
        full_item_path = build_path(item, path)
        if filter_fn(full_item_path):
            yield full_item_path


def get_markdown_files(filenames):
    for filename in filenames:
        if MARKDOWN_FILTER.search(filename):
            yield filename


def standardize_filename(filename):
    return TEMPLATED_FILENAME_FILTER.sub(
        '-',
        TRAILING_SUFFIX.sub(
            '',
            LEADING_SLASHES.sub('', filename)))


def build_tags(path):
    # process files looking at Meta for tags
    # create list of namedtuples with title: tag
    # use this to create index of titles for each tag
    pass


def convert_date_time(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def prepare_target_dir():
    # extract contents of if
    def setup_target_dir():
        os.mkdir(TARGET_DIR, 0755)
        copytree(STATIC_DIR, os_path.join(TARGET_DIR, './static'))

    if not os_path.exists(TARGET_DIR):
        setup_target_dir()
        return

    if os_path.isdir(TARGET_DIR):
        if ARGS.delete:
            rmtree(TARGET_DIR)
            setup_target_dir()
        else:
            exit()


def set_settings(args):
    global ARGS
    global TARGET_DIR
    if args.target:
        TARGET_DIR = args.target
    ARGS = args


if __name__ == '__main__':
    # add logger here
    # align functions top to bottom
    # analyze in term of abstraction level mixing
    # pull out into other modules
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delete',
                        help=("Remove target output directory before "
                              "generating. Default: {}").format(
                                  TARGET_DIR),
                        action='store_true')
    parser.add_argument('-t', '--target',
                        help=("Change target output directory."
                              "Default: {}").format(TARGET_DIR))

    set_settings(parser.parse_args())

    prepare_target_dir()
    build_tree('./')

    with open(os_path.join(TARGET_DIR, 'feed'), 'wb') as f:
        f.write(FEED.generate_xml())
