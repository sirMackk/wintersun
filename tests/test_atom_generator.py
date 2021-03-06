import pytest

from wintersun import atom_generator


@pytest.fixture
def feed_settings():
    return [
        {'name': 'title',
         'value': 'feed-title'},
        {'name': 'link',
         'attributes': {
            'rel': 'self',
            'href': 'http://testing.example.com/'}},
        {'name': 'link',
         'attributes': {
             'rel': 'alternate',
             'href': 'http://testing.example.com'}},
        {'name': 'id',
         'value': 'http://testing.example.com/'},
        {'name': 'updated',
         'value': '2015-06-17T00:00:00-06:00'}]


@pytest.fixture
def feed(feed_settings):
    title = feed_settings[0]['value']
    url = feed_settings[2]['attributes']['href']
    ts = feed_settings[-1]['value']
    feed = atom_generator.Feed(title, url, ts)
    return feed


class TestFeed:
    entry = {
            'title': 'test-entry',
            'link': 'http://blog.com/entry-1',
            'published': '2015-06-15T00:00:00-06:00',
            'updated': '2015-06-15T00:00:00-06:00',
            'name': 'author-name',
            'content': "This is a testing entry " * 10}

    def test_init_feed(self, feed, feed_settings):
        assert feed.settings == feed_settings

    def test_one_entry(self, feed):
        feed.add_entry(self.entry)
        result_xml = feed.generate_xml()

        assert result_xml.count('test-entry') == 1
        assert result_xml.count('author-name') == 1
        assert result_xml.count('blog.com/entry-1') == 2
        assert result_xml.count('testing entry') == 10
        assert result_xml.count('2015-06-15T00:00:00-06:00') == 2

    def test_multiple_entries(self, feed):
        entry = self.entry.copy()
        entry2 = self.entry.copy()
        feed.add_entry(entry)

        entry2['title'] = 'New Title'
        entry2['link'] = 'http://blog.com/entry-2'
        entry2['published'] = '2015-06-13T00:00:00-06:00'
        entry2['updated'] = entry2['published']
        entry2['content'] = 'New Content! ' * 5

        feed.add_entry(entry2)
        result_xml = feed.generate_xml()

        assert result_xml.count('New Title') == 1
        assert result_xml.count('author-name') == 2
        assert result_xml.count('blog.com/entry-2') == 2
        assert result_xml.count('New Content!') == 5
        assert result_xml.count('2015-06-13T00:00:00-06:00') == 2
