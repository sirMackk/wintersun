import argparse
import configparser
import logging
import os
import os.path as os_path
import re
from collections import defaultdict, namedtuple
from datetime import datetime
from shutil import copytree, rmtree
from sys import exit, stdout

from jinja2 import Environment, FileSystemLoader

from wintersun.atom_generator import Feed, create_timestamp
from wintersun.transformers import CachingTransformer, MarkdownTransformer

CONFIG = None
FEED = None


def get_config(path):
    parser = configparser.ConfigParser()
    parser.read(path)
    config = dict(parser['DEFAULT'])
    if 'excluded_dirs' in config:
        excluded_dirs = config['excluded_dirs'].split(',')
        config['excluded_dirs'] = [e_dir.strip() for e_dir in excluded_dirs]

    config['template_env'] = get_template_env(config['template_dir'])
    return config


def get_template_env(template_dir):
    # integration test
    return Environment(loader=FileSystemLoader(template_dir))


MARKDOWN_FILTER = re.compile(r'([a-zA-Z0-9_-]+)\.md')
TEMPLATED_FILENAME_FILTER = re.compile(r'[^a-z^A-Z^0-9-]')
LEADING_SLASHES = re.compile(r'^[a-zA-Z0-9\.\/]*\/')
RELATIVE_SLASHES = re.compile(r'\./(?![a-zA-Z])')
TRAILING_SUFFIX = re.compile(r'\.md$')

OUTPUT_ENCODING = 'utf-8-sig'

PostItem = namedtuple('PostItem', 'filename, title, date, tags')
TRANSFORMER = CachingTransformer(MarkdownTransformer)


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stdout))
logger.setLevel(logging.INFO)


def build_tree(path):
    directories, input_files = get_files_and_directories_from(path)

    for md_file in input_files:
        logger.info('input file: %s', md_file)
        transform_into_output(md_file, path)

    transform_next_dir_level(path, directories)


def get_files_and_directories_from(dir_path):
    directories = filter_items_from_path(dir_path, filter_fn=os_path.isdir)
    md_files = get_markdown_files(
        filter_items_from_path(dir_path, filter_fn=os_path.isfile))
    return directories, md_files


def transform_into_output(md_file, path):
    content, meta = TRANSFORMER.get_or_create(path, md_file)
    write_output_file(apply_template(content, meta), meta)


def apply_template(contents, meta):
    templated_item = render_template(contents, meta)

    return templated_item


def apply_transformer(transformer, filename):
    with open(filename) as f:
        return transformer.convert_utf8(f)


def is_template(template_type, meta):
    return meta['template'] == template_type.capitalize()


def render_template(contents, meta):
    logger.info('template meta title: %s', meta['title'])
    template = get_template(meta['template'])
    if is_template('index', meta) or is_template('main', meta):
        meta['indexed'], meta['indexed_dir'] = generate_post_index(meta)

    return template.render(
        contents=contents,
        meta=meta)


def get_template(title):
    return CONFIG['template_env'].get_template(title.lower() + '.html')


def write_output_file(contents, meta):
    path = meta['path']
    out_filename = standardize_filename(meta['filename'].strip()) + '.html'

    logger.info('creating file: %s',
                out_filename)

    output_destination_path = os_path.join(
        CONFIG['target_dir'],
        path,
        out_filename)

    with open(output_destination_path, mode='wb') as out:
        out.write(contents.encode(OUTPUT_ENCODING))


def transform_next_dir_level(path, directories):
    for directory in directories:
        all_excluded_dirs = CONFIG['excluded_dirs'] + [
            CONFIG['template_dir'], CONFIG['static_dir'], CONFIG['target_dir']]
        all_excluded_dirs = [
            os_path.join(path, directory) for directory in all_excluded_dirs
        ]
        if directory not in all_excluded_dirs:
            new_dir_path = os_path.join(CONFIG['target_dir'], path, directory)
            logger.info('making dir: %s at %s', directory, new_dir_path)
            os.mkdir(new_dir_path, 0o755)
            build_tree(os_path.join(path, directory))


def generate_post_index(meta):
    index_directory_name = MARKDOWN_FILTER.search(meta['filename']).groups()

    if not index_directory_name:
        return []

    index_directory_path = os_path.join(meta['path'], index_directory_name[0])
    return filenames_by_date(index_directory_path), index_directory_path


def filenames_by_date(dir_path):
    files = []
    _, input_files = get_files_and_directories_from(dir_path)

    for input_file in input_files:
        _, meta = TRANSFORMER.get_or_create(dir_path, input_file)
        files.append(create_postitem(input_file, meta))

    return sorted(
        files,
        key=lambda post_item: post_item.date,
        reverse=True)


def create_postitem(file_name, file_meta):
    return PostItem._make((
        standardize_filename(file_name),
        file_meta['title'],
        convert_date_time(file_meta['date']),
        file_meta['tags'],))


def convert_date_time(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def generate_atom_entry_dict(contents, meta):
    entry = {
        'title': meta['title'],
        'link': generate_entry_link(meta['filename'], meta['path']),
        'published': create_timestamp(meta['date']),
        'updated': create_timestamp(meta['date']),
        'name': CONFIG['author'],
        'content': contents[:100] + '...'}

    return entry


def generate_entry_link(md_file, path):
    return '/'.join(
        [CONFIG['site_url'],
         path.replace('./', ''),
         standardize_filename(md_file) + '.html'])


def filter_items_from_path(path, filter_fn=os_path.isfile):
    for item in os.listdir(path):
        full_item_path = build_path(item, path)
        if filter_fn(full_item_path):
            yield RELATIVE_SLASHES.sub('', full_item_path)


def build_path(node, path):
    return os_path.join(path, node)


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


def generate_tag_index(tag, items):
    template = get_template('tag')
    rendered = template.render(
        tag=tag,
        tagged_items=items
    )

    dest = os_path.join(CONFIG['target_dir'], CONFIG['tag_dir'], tag + '.html')
    logger.info('Writing %s tag to %s', tag, dest)
    with open(dest, 'wb') as f:
        f.write(rendered.encode('utf-8-sig'))


def build_tags(items):
    tags = defaultdict(list)
    for _, meta in items:
        for tag in meta['tags'].split():
            tags[tag].append({
                'title': meta['title'],
                'link':  generate_entry_link(meta['filename'], meta['path']),
                'date': meta['date']
            })

    for tag, items in tags.items():
        generate_tag_index(
            tag,
            sorted(items, key=lambda item: item['date'], reverse=True))


def prepare_target_dir():
    target_dir = CONFIG['target_dir']
    tag_dir = CONFIG['tag_dir']
    delete_target_dir = CONFIG['delete_target_dir']
    static_dir = CONFIG['static_dir']

    def setup_target_dir():
        os.mkdir(target_dir, 0o755)
        os.mkdir(os_path.join(target_dir, tag_dir), 0o755)
        copytree(static_dir, os_path.join(target_dir, './static'))

    if not os_path.exists(target_dir):
        setup_target_dir()
        return

    if os_path.isdir(target_dir):
        if delete_target_dir:
            rmtree(target_dir)
            setup_target_dir()
        else:
            exit()


def create_rss_feed(config, items):
    feed = Feed([
        {'name': 'title',
         'value': 'mattscodecave.com'},
        {'name': 'link',
            'attributes': {
                'rel': 'self',
                'href': config['site_url'] + '/'}},
        {'name': 'link',
            'attributes': {
                'rel': 'alternate',
                'href': config['site_url']}},
        {'name': 'id',
            'value': config['site_url'] + '/'},
        {'name': 'updated',
            'value': create_timestamp()}])
    with open(os_path.join(CONFIG['target_dir'], 'feed'), 'w') as f:
        for content, meta in items:
            if is_template('post', meta):
                feed.add_entry(generate_atom_entry_dict(content, meta))
        f.write(feed.generate_xml())


def main():
    global CONFIG
    # add setup py
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', help='INI file containing blog config')
    parser.add_argument(
        '-d',
        '--delete',
        default=False,
        help=("Remove target output directory before "
              "generating. Default: {}").format(False),
        action='store_true')
    parser.add_argument(
        '-t',
        '--target',
        help=("Change target output directory."
              "Default: {}").format('site'))

    args = parser.parse_args()
    CONFIG = get_config(args.manifest)
    CONFIG['delete_target_dir'] = args.delete

    # pull out into own function

    prepare_target_dir()
    build_tree('./')

    create_rss_feed(CONFIG, TRANSFORMER.cache.values())

    build_tags(TRANSFORMER.cache.values())
