import unittest
import mock

import atom_generator

class TestFeed(unittest.TestCase):

    def test_init_feed(self):
        settings = [
            {'name': 'title',
            'value': 'feed-title'},
            {'name': 'link',
            'attributes': {
                'rel': 'self',
                'href': 'http://test.example.com'}},
            {'name': 'link',
                'attributes': {
                'rel': 'alternate',
                'href': 'http://testing.example.com'}},
            {'name': 'id',
            'value': 'http://testing.example.com'},
            {'name': 'updated',
            'value': '2015-06-17T00:00:00-06:00'}]
        feed = atom_generator.Feed(settings)
        self.assertEqual(feed.settings, settings)
        # add assertions to test this object

        # test structure

        # test xml?


if __name__ == '__main__':
    unittest.main()
