import logging
import textwrap
import unittest
from unittest import mock

import pytest

from wintersun import wintersun

logging.disable(logging.INFO)


dummy_config = {
        'target_dir': 'some_dir',
        'tag_dir': 'tag_dir',
        'delete_target_dir': False,
        'static_dir': 'static_dir',
        'author': 'Matt',
        'site_url': 'http://example.com',
        'template_dir': 'template_dir',
        'template_env': mock.Mock(),
        'excluded_dirs': ['ex_dir1', 'ex_dir2']
    }


@pytest.fixture
def conf():
    return dummy_config


class TestWintersun(unittest.TestCase):

    def setUp(self):
        self.config = dummy_config.copy()

    def test_get_markdown_files(self):
        markdown_files = list(wintersun.get_markdown_files(
            ['test1.md', 'test2.html', 'test3.m', 'test4md.txt']))
        self.assertEqual(markdown_files, ['test1.md'])

    @mock.patch('wintersun.wintersun.os_path')
    @mock.patch('wintersun.wintersun.os')
    def test_filter_items_from_path_dirs(self, mock_os, mock_os_path):
        mock_os.listdir.return_value = ['file1', 'dir1']
        mock_os_path.isdir.side_effect = lambda full_path: full_path == 'dir1'
        mock_os_path.join.side_effect = lambda path, filename: filename

        dirs = list(wintersun.filter_items_from_path(
            './current-dir',
            mock_os_path.isdir))

        self.assertEqual(mock_os_path.join.call_count, 2)
        self.assertEqual(mock_os_path.isdir.call_count, 2)
        mock_os.listdir.assert_called_with('./current-dir')
        self.assertEqual(dirs, ['dir1'])

    @mock.patch('wintersun.wintersun.os_path')
    @mock.patch('wintersun.wintersun.os')
    def test_filter_items_from_path_files(self, mock_os, mock_os_path):
        mock_os.listdir.return_value = ['file1', 'dir1']
        mock_os_path.isfile.side_effect = lambda x: x == 'file1'
        mock_os_path.join.side_effect = lambda x, y: y

        files = list(wintersun.filter_items_from_path(
            './current-dir',
            mock_os_path.isfile))

        self.assertEqual(mock_os_path.join.call_count, 2)
        mock_os.listdir.assert_called_with('./current-dir')
        self.assertEqual(files, ['file1'])

    def test_standardize_filename_with_leading_slashes(self):
        filepath = '/home/test/files/markdown.md'
        self.assertEqual(
            wintersun.standardize_filename(filepath), 'markdown')

    def test_standardize_filename_with_relative_slashes(self):
        filepath = './tests/markdown.md'
        self.assertEqual(
            wintersun.standardize_filename(filepath), 'markdown')

    def test_standardize_filename_with_trailing_suffix(self):
        filepath = '/home/test/files/markdown.md'
        self.assertEqual(
            wintersun.standardize_filename(filepath), 'markdown')

    @mock.patch('wintersun.wintersun.filenames_by_date')
    def test_generate_post_index(self, mock_filenames_by_date):
        mock_filenames_by_date.return_value = ('file1', 'file2',)
        dir_path = './wintersun/posts'
        meta = {'filename': 'posts.md', 'path': dir_path}

        files, path = wintersun.generate_post_index(meta)
        self.assertEqual(dir_path + '/posts', path)
        self.assertIn('file1', files)
        self.assertIn('file2', files)

    @mock.patch('wintersun.transformers.open', mock.mock_open())
    @mock.patch('wintersun.wintersun.TRANSFORMER.get_or_create')
    @mock.patch('wintersun.wintersun.filter_items_from_path')
    def test_filenames_by_date(self, mock_filter_items_from_path,
                               mock_get_or_create):
        mock_filter_items_from_path.return_value = (
            'file1.md',
            'file2.md',
        )
        mock_get_or_create.side_effect = [
            (None, {
                'title': 'title1',
                'date': '2015-09-22 20:00:00',
                'tags': ['none']}),
            (None, {
                'title': 'title2',
                'date': '2015-08-22 20:00:00',
                'tags': ['none']})
        ]

        sorted_filenames = wintersun.filenames_by_date('./posts')
        self.assertEqual(sorted_filenames[0].title, 'title1')
        self.assertEqual(sorted_filenames[1].title, 'title2')

    def test_generate_entry_link(self):
        file_name = 'file1'
        path = './wintersun/posts'
        with mock.patch.object(wintersun, 'CONFIG', self.config):
            link = wintersun.generate_entry_link(file_name, path)
        self.assertEqual(
            link, self.config['site_url'] + '/wintersun/posts/file1.html')

    def test_generate_atom_entry_dict(self):
        meta = {'title': 'title1',
                'date': '2015-09-22',
                'filename': 'file1',
                'path': './wintersun/posts'}
        contents = 'Lorem ipsum ' * 25
        expected_result = {
            'title': meta['title'],
            'link': self.config['site_url'] + '/wintersun/posts/file1.html',
            'published': '2015-09-22T00:00:00+01:00',
            'updated': '2015-09-22T00:00:00+01:00',
            'name': 'Matt',
            'content': contents[:100] + '...'}

        with mock.patch.object(wintersun, 'CONFIG', self.config):
            entry = wintersun.generate_atom_entry_dict(contents, meta)

            self.assertEqual(entry, expected_result)

    @mock.patch('wintersun.wintersun.os_path.join')
    def test_build_path(self, mock_os_path):
        wintersun.build_path('file1', './wintersun/posts')
        self.assertTrue(mock_os_path.called)

    def test_write_output_file(self):
        with mock.patch('builtins.open', mock.mock_open()) as mock_open:
            target_dir = self.config['target_dir'] = 'target'
            meta = {'path': 'wintersun/posts', 'filename': 'file1'}

            with mock.patch.object(wintersun, 'CONFIG', self.config):
                wintersun.write_output_file('', meta)
                mock_open.assert_called_with(
                    target_dir + '/' + meta['path'] + '/' + 'file1.html',
                    mode='wb')
                self.assertTrue(mock_open().__enter__().write.called)

    def test_render_template_post(self):
        mock_template = mock.Mock()

        meta = {'title': 'title', 'template': 'Post',
                'filename': 'file1.md', 'path': 'wintersun/posts'}
        contents = 'Lorem ipsum ' * 100

        with mock.patch.object(wintersun, 'CONFIG', self.config) as conf:
            conf['template_env'].get_template.return_value = mock_template
            wintersun.render_template(contents, meta)
            conf['template_env'].get_template.assert_called_with('post.html')
            self.assertTrue(mock_template.render.called)

    @mock.patch('wintersun.wintersun.generate_post_index')
    def test_render_template_index(self, mock_gen_post_index):
        mock_gen_post_index.return_value = (1, 2,)
        meta = {'title': 'title', 'template': u'Index',
                'filename': 'file1.md', 'path': 'wintersun/posts'}
        contents = 'Lorem ipsum ' * 100

        with mock.patch.object(wintersun, 'CONFIG', self.config) as conf:
            wintersun.render_template(contents, meta)
            self.assertTrue(mock_gen_post_index.called)

    @mock.patch('wintersun.wintersun.build_tree')
    def test_transform_next_dir_level_no_directories(self, mock_build_tree):
        path = 'wintersun/posts'
        directories = []

        wintersun.transform_next_dir_level(path, directories)

        self.assertFalse(mock_build_tree.called)

    @mock.patch('wintersun.wintersun.os.mkdir')
    @mock.patch('wintersun.wintersun.build_tree')
    def test_transform_next_dir_level_excluded_dirs(self, mock_build_tree,
                                                    mock_mkdir):
        path = './'
        rel_excluded_dirs = [
            path + directory for directory in self.config['excluded_dirs']
        ]

        with mock.patch.object(wintersun, 'CONFIG', self.config):
            wintersun.transform_next_dir_level(path,
                                               rel_excluded_dirs)
            self.assertFalse(mock_build_tree.called)

    @mock.patch('wintersun.wintersun.os.mkdir')
    @mock.patch('wintersun.wintersun.build_tree')
    def test_transform_next_dir_level(self, mock_build_tree, mock_mkdir):
        path = 'wintersun/posts'
        directories = ['dir1', 'dir2']
        # expected_path = self.config['target_dir'] = '/' + path
        expected_path = self.config['target_dir'] + '/' + path

        with mock.patch.object(wintersun, 'CONFIG', self.config):
            wintersun.transform_next_dir_level(path, directories)

        mock_mkdir.assert_has_calls([mock.call(expected_path + '/dir1', 0o755),
                                     mock.call(expected_path + '/dir2', 0o755)])
        self.assertTrue(mock_build_tree.called)

    @mock.patch('builtins.open')
    @mock.patch('wintersun.wintersun.transform_next_dir_level')
    @mock.patch('wintersun.wintersun.filter_items_from_path')
    @mock.patch('wintersun.wintersun.MarkdownTransformer')
    @mock.patch('wintersun.wintersun.render_template')
    @mock.patch('wintersun.wintersun.write_output_file')
    def test_build_tree(self, mock_write_output_file,
                        mock_render_template, mock_md_tranformer,
                        mock_filter_items_from_path,
                        mock_transform_next_dir_level, mock_open):
        mock_filter_items_from_path.side_effect = [[], ['file1.md', 'file2.md']
                                                   ]
        wintersun.build_tree('wintersun/posts')

        self.assertEqual(mock_render_template.call_count, 2)
        self.assertEqual(mock_write_output_file.call_count, 2)
        self.assertTrue(mock_transform_next_dir_level.called)

    @mock.patch('wintersun.wintersun.copytree')
    @mock.patch('wintersun.wintersun.os.mkdir')
    @mock.patch('wintersun.wintersun.os_path')
    @mock.patch('wintersun.wintersun.rmtree')
    def test_prepare_target_dir_target_dir_exists(self, mock_rmtree,
                                                  mock_os_path, mock_mkdir,
                                                  mock_copytree):
        with mock.patch.object(wintersun, 'CONFIG', self.config) as conf:
            mock_os_path.exists.return_value = True
            mock_os_path.isdir.return_value = True
            conf['delete_target_dir'] = True

            wintersun.prepare_target_dir()

            self.assertTrue(mock_rmtree.called)
            self.assertTrue(mock_mkdir.called)
            self.assertTrue(mock_copytree.called)

    @mock.patch('wintersun.wintersun.copytree')
    @mock.patch('wintersun.wintersun.os.mkdir')
    @mock.patch('wintersun.wintersun.os_path')
    def test_prepare_target_dir_target_dir_dont_exist(self,
                                                      mock_os_path,
                                                      mock_mkdir,
                                                      mock_copytree):
        with mock.patch.object(wintersun, 'CONFIG', self.config) as conf:
            mock_os_path.exists.return_value = False

            wintersun.prepare_target_dir()

            self.assertTrue(mock_mkdir.called)
            self.assertTrue(mock_copytree.called)

    @mock.patch('wintersun.wintersun.filter_items_from_path')
    def test_get_files_and_directories_from(self, mock_filter_items):
        mock_filter_items.side_effect = [
            ['dir1', 'dir2'],
            ['file1.md', 'file2.md']
        ]

        d, f = wintersun.get_files_and_directories_from('wintersun/posts')

        self.assertEqual(mock_filter_items.call_count, 2)
        self.assertEqual(d, ['dir1', 'dir2'])
        self.assertEqual(list(f), ['file1.md', 'file2.md'])


@pytest.fixture
def mock_config(tmpdir):
    config = tmpdir.join('mock_manifest.ini')
    config.write(textwrap.dedent(
    """ [DEFAULT]
        site_url = http://example.com
        template_dir = templates
        static_dir = static
        target_dir = site
        tag_dir = tags
        excluded_dirs = media,.git
        feed_title = example.com
        log_level = info"""))
    return config


def test_get_config_file(mocker, mock_config):
    mocker.patch.object(wintersun, 'get_template_env', return_value='env')
    cfg = wintersun.get_config(mock_config.strpath)
    expected = {
        'site_url': 'http://example.com',
        'template_dir': 'templates',
        'static_dir': 'static',
        'target_dir': 'site',
        'tag_dir': 'tags',
        'excluded_dirs': ['media', '.git'],
        'feed_title': 'example.com',
        'log_level': 'info',
        'template_env': 'env'
    }
    assert cfg == expected


if __name__ == '__main__':
    unittest.main()
