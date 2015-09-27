import unittest
import mock
import logging

import wintersun

logging.disable(logging.INFO)


class TestWintersun(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_markdown_files(self):
        markdown_files = list(wintersun.get_markdown_files(
            ['test1.md', 'test2.html', 'test3.m', 'test4md.txt']))
        self.assertEqual(markdown_files, ['test1.md'])

    @mock.patch('wintersun.os_path')
    @mock.patch('wintersun.os')
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

    @mock.patch('wintersun.os_path')
    @mock.patch('wintersun.os')
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

    @mock.patch('wintersun.filenames_by_date')
    def test_generate_post_index(self, mock_filenames_by_date):
        mock_filenames_by_date.return_value = ('file1', 'file2',)
        dir_path = './wintersun/posts'
        files, path = wintersun.generate_post_index('posts.md', dir_path)
        self.assertEqual(dir_path + '/posts', path)
        self.assertIn('file1', files)
        self.assertIn('file2', files)

    @mock.patch('__builtin__.open')
    @mock.patch('wintersun.MarkdownTransformer')
    @mock.patch('wintersun.filter_items_from_path')
    def test_filenames_by_date(self, mock_filter_items_from_path,
                               mock_transformer, mock_open):

        mock_filter_items_from_path.return_value = ('file1.md', 'file2.md', )

        mock_transformer.return_value.__enter__.return_value = mock_transformer
        type(mock_transformer).Meta = mock.PropertyMock(side_effect=[
            {'title': ['title1'],
                'date': ['2015-09-22 20:00:00']},
            {'title': ['title2'],
                'date': ['2015-08-22 20:00:00']}
        ])

        sorted_filenames = wintersun.filenames_by_date('./posts')
        self.assertEqual(sorted_filenames[0].title, 'title1')
        self.assertEqual(sorted_filenames[1].title, 'title2')

    def test_generate_entry_link(self):
        file_name = 'file1'
        path = './wintersun/posts'
        link = wintersun.generate_entry_link(file_name, path)
        self.assertEqual(link,
                         wintersun.SITE_URL + '/wintersun/posts/file1.html')

    def test_generate_atom_entry_dict(self):
        meta = {'title': ['title1'],
                'date': ['2015-09-22']}
        contents = 'Lorem ipsum ' * 25
        file_name = 'file1'
        path = './wintersun/posts'
        expected_result = {
            u'title': meta['title'][0],
            u'link': wintersun.SITE_URL + '/wintersun/posts/file1.html',
            u'published': '2015-09-22T00:00:00+01:00',
            u'updated': '2015-09-22T00:00:00+01:00',
            u'name': u'Matt',
            u'content': contents[:100] + '...'}

        entry = wintersun.generate_atom_entry_dict(contents, file_name, path,
                                                   meta)

        self.assertEqual(entry, expected_result)

    @mock.patch('wintersun.generate_atom_entry_dict')
    def test_update_feed(self, mock_entry_dict):
        feed = mock.Mock()

        wintersun.update_feed(feed, '', 'file1', 'wintersun/', {})
        self.assertTrue(mock_entry_dict.called)
        self.assertTrue(feed.add_entry.called)

    @mock.patch('wintersun.os_path.join')
    def test_build_path(self, mock_os_path):
        wintersun.build_path('file1', './wintersun/posts')
        self.assertTrue(mock_os_path.called)

    @mock.patch('__builtin__.open')
    def test_write_output_file(self, mock_open):
        target_dir = wintersun.TARGET_DIR = 'target'
        path = 'wintersun/posts'
        filename = 'file1'

        wintersun.write_output_file(path, filename, '')
        mock_open.assert_called_with(target_dir + '/' + path + '/' +
                                     'file1.html', mode='w')
        self.assertTrue(mock_open().__enter__().write.called)

    @mock.patch('wintersun.env')
    def test_apply_output_template_post(self, mock_env):
        mock_template = mock.Mock()
        mock_env.get_template.return_value = mock_template

        file_name = 'file1.md'
        path = 'wintersun/posts'
        meta = {'title': ['title'], 'template': ['Post']}
        contents = 'Lorem ipsum ' * 100

        wintersun.apply_output_template(file_name, path, contents, meta)
        self.assertTrue(mock_env.get_template.called)
        self.assertTrue(mock_template.render.called)

    @mock.patch('wintersun.env')
    @mock.patch('wintersun.generate_post_index')
    def test_apply_output_template_index(self, mock_gen_post_index, mock_env):
        mock_gen_post_index.return_value = (1, 2,)
        file_name = 'file1.md'
        path = 'wintersun/posts'
        meta = {'title': ['title'], 'template': ['Index']}
        contents = 'Lorem ipsum ' * 100

        wintersun.apply_output_template(file_name, path, contents, meta)
        self.assertTrue(mock_gen_post_index.called)

    @mock.patch('wintersun.build_tree')
    def test_transform_next_dir_level_no_directories(self, mock_build_tree):
        path = 'wintersun/posts'
        directories = []

        wintersun.transform_next_dir_level(path, directories)

        self.assertFalse(mock_build_tree.called)

    @mock.patch('wintersun.build_tree')
    def test_transform_next_dir_level_excluded_dirs(self, mock_build_tree):
        path = 'wintersun/posts'

        wintersun.transform_next_dir_level(path, wintersun.EXCLUDED_DIRS)
        self.assertFalse(mock_build_tree.called)

    @mock.patch('wintersun.os.mkdir')
    @mock.patch('wintersun.build_tree')
    def test_transform_next_dir_level(self, mock_build_tree, mock_mkdir):
        path = 'wintersun/posts'
        directories = ['dir1', 'dir2']
        expected_path = wintersun.TARGET_DIR = '/' + path

        wintersun.transform_next_dir_level(path, directories)

        mock_mkdir.assert_has_call([mock.call(expected_path + '/dir1'),
                                    mock.call(expected_path + '/dir2')])
        self.assertTrue(mock_build_tree.called)

    @mock.patch('__builtin__.open')
    @mock.patch('wintersun.transform_next_dir_level')
    @mock.patch('wintersun.filter_items_from_path')
    @mock.patch('wintersun.MarkdownTransformer')
    @mock.patch('wintersun.apply_output_template')
    @mock.patch('wintersun.write_output_file')
    def test_build_tree(self, mock_write_output_file,
                        mock_apply_output_template, mock_md_tranformer,
                        mock_filter_items_from_path,
                        mock_transform_next_dir_level, mock_open):
        mock_filter_items_from_path.side_effect = [[], ['file1.md', 'file2.md']
                                                   ]

        wintersun.build_tree('wintersun/posts')

        self.assertEqual(mock_apply_output_template.call_count, 2)
        self.assertEqual(mock_write_output_file.call_count, 2)
        self.assertTrue(mock_transform_next_dir_level.called)

    @mock.patch('wintersun.copytree')
    @mock.patch('wintersun.os.mkdir')
    @mock.patch('wintersun.os_path')
    @mock.patch('wintersun.rmtree')
    @mock.patch('wintersun.ARGS')
    def test_prepare_target_dir_target_dir_exists(self, mock_ARGS, mock_rmtree,
                                                  mock_os_path, mock_mkdir,
                                                  mock_copytree):
        mock_os_path.exists.return_value = True
        mock_os_path.isdir.return_value = True
        mock_ARGS.delete = mock.PropertyMock(return_value=True)

        wintersun.prepare_target_dir()

        self.assertTrue(mock_rmtree.called)
        self.assertTrue(mock_mkdir.called)
        self.assertTrue(mock_copytree.called)

    @mock.patch('wintersun.copytree')
    @mock.patch('wintersun.os.mkdir')
    @mock.patch('wintersun.os_path')
    def test_prepare_target_dir_target_dir_dont_exist(self,
                                                      mock_os_path,
                                                      mock_mkdir,
                                                      mock_copytree):
        mock_os_path.exists.return_value = False

        wintersun.prepare_target_dir()

        self.assertTrue(mock_mkdir.called)
        self.assertTrue(mock_copytree.called)


class TestMarkdownTransformer(unittest.TestCase):

    @mock.patch('wintersun.markdown.Markdown')
    def test_convert_utf8(self, mock_md):
        flike = mock.Mock()
        flike.read.return_value = 'test\n'
        md_instance_mock = mock.Mock()
        mock_md.return_value = md_instance_mock
        md = wintersun.MarkdownTransformer()

        md.convert_utf8(flike)

        self.assertTrue(flike.read.called)
        self.assertTrue(md_instance_mock.convert.called)

    @mock.patch('wintersun.markdown.Markdown')
    def test_md_transformer_reset(self, mock_md):
        with wintersun.MarkdownTransformer() as md:
            md.Meta

        self.assertTrue(mock_md.called)
        self.assertTrue(mock_md().reset.called)




if __name__ == '__main__':
    unittest.main()
