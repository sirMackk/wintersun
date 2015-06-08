import unittest
import mock

import wintersun


class TestWintersun(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_markdown_files(self):
        markdown_files = list(wintersun.get_markdown_files(
            ['test1.md', 'test2.html', 'test3.m', 'test4md.txt']))
        self.assertEqual(markdown_files, ['test1.md'])

    @mock.patch('wintersun.os_path')
    @mock.patch('wintersun.os')
    def test_get_items_from_path_dirs(self, mock_os, mock_os_path):
        mock_os.listdir.return_value = ['file1', 'dir1']
        mock_os_path.isdir.side_effect = lambda full_path: full_path == 'dir1'
        mock_os_path.join.side_effect = lambda path, filename: filename

        dirs = list(wintersun.get_items_from_path(
            './current-dir',
            mock_os_path.isdir))

        self.assertEqual(mock_os_path.join.call_count, 2)
        self.assertEqual(mock_os_path.isdir.call_count, 2)
        mock_os.listdir.assert_called_with('./current-dir')
        self.assertEqual(dirs, ['dir1'])

    @mock.patch('wintersun.os_path')
    @mock.patch('wintersun.os')
    def test_get_items_from_path_files(self, mock_os, mock_os_path):
        mock_os.listdir.return_value = ['file1', 'dir1']
        mock_os_path.isfile.side_effect = lambda x: x == 'file1'
        mock_os_path.join.side_effect = lambda x, y: y

        files = list(wintersun.get_items_from_path(
            './current-dir',
            mock_os_path.isfile))

        self.assertEqual(mock_os_path.join.call_count, 2)
        mock_os.listdir.assert_called_with('./current-dir')
        self.assertEqual(files, ['file1'])

if __name__ == '__main__':
    unittest.main()
