import argparse
import configparser
from pathlib import Path
from shutil import copytree, rmtree

from wintersun import post_reader, post_repo, presenters, renderers


def _prepare_target_dir(target_dir, static_dir, delete_target_dir=False):
    if delete_target_dir and target_dir.exists():
        rmtree(target_dir)

    if not target_dir.exists():
        target_dir.mkdir(mode=0o755)

    copytree(static_dir, target_dir / 'static')


def _get_config(path):
    parser = configparser.ConfigParser()
    parser.read(path)
    config = dict(parser['DEFAULT'])
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', help='INI file containing blog config')
    parser.add_argument(
        '-d',
        '--delete',
        default=False,
        help=("Remove target output directory before "
              "generating. Default: {}").format(False),
        action='store_true')

    args = parser.parse_args()
    config = _get_config(args.manifest)

    target_dir = Path(config['target_dir'])
    static_dir = Path(config['static_dir'])
    _prepare_target_dir(target_dir, static_dir,
                        config['delete_target_dir'])

    repo = post_repo.InMemPostRepo()
    for post in post_reader.MdFileReader.read('.'):
        repo.insert(**post)

    atom_feed = presenters.AtomPresenter(
        config['feed_title'], config['site_url'], config['post_dir'],
        config['author'], config['encoding'])
    atom_feed.output(repo.all(), target_dir / 'feed')

    renderer = renderers.TemplateRenderer(config['template_dir'])
    tags = presenters.TagPresenter(renderer, config['site_url'],
                                   config['post_dir'])
    tags.output(repo.all(), target_dir / config['tag_dir'])

    pages = presenters.HTMLPresenter(renderer)

    pages.output(repo.all(), target_dir / config['post_dir'])
