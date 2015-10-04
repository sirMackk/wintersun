import unittest
import mock
from StringIO import StringIO

from transformers import MarkdownTransformer


class TestMarkdownTransformer(unittest.TestCase):
    def setUp(self):
        self.f_like = StringIO()
        self.f_like.write('Prop1: 1\nProp2: two\n\nThis is text\n')
        self.f_like.seek(0)

    def test_convert_utf8(self):
        flike = mock.Mock()
        flike.read.return_value = 'test\n'
        with MarkdownTransformer() as md:
            converted = md.convert_utf8(flike)

            self.assertTrue(flike.read.called)
            self.assertEqual(converted, '<p>test</p>')

    @mock.patch('markdown.Markdown')
    def test_md_transformer_reset(self, mock_md):
        with MarkdownTransformer() as md:
            md.Meta

        self.assertTrue(mock_md.called)
        self.assertTrue(mock_md().reset.called)

    def test_Meta(self):
        md = MarkdownTransformer()
        md.convert_utf8(self.f_like)

        self.assertEqual(md.Meta['prop1'], '1')
        self.assertEqual(md.Meta['prop2'], 'two')

    def test_assign_Meta_before_convert(self):
        md = MarkdownTransformer()
        md.Meta['test1'] = 'one'
        md.convert_utf8(self.f_like)

        self.assertEqual(md.Meta['test1'], 'one')
        self.assertEqual(md.Meta['prop1'], '1')
        self.assertEqual(md.Meta['prop2'], 'two')

    def test_assign_Meta_after_convert(self):
        md = MarkdownTransformer()
        md.convert_utf8(self.f_like)
        md.Meta['test1'] = 'one'

        self.assertEqual(md.Meta['prop1'], '1')
        self.assertEqual(md.Meta['prop2'], 'two')


if __name__ == '__main__':
    unittest.main()
