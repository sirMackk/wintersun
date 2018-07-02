import unittest
from io import StringIO
from unittest import mock

from wintersun.transformers import MarkdownTransformer


class TestMarkdownTransformer(unittest.TestCase):
    def setUp(self):
        self.f_like = StringIO()
        self.f_like.write('Prop1: 1\nProp2: two\n\nThis is text\n')
        self.f_like.seek(0)

    @mock.patch('markdown.Markdown')
    def test_md_transformer_reset(self, mock_md):
        with MarkdownTransformer():
            pass

        self.assertTrue(mock_md.called)
        self.assertTrue(mock_md().reset.called)


if __name__ == '__main__':
    unittest.main()
