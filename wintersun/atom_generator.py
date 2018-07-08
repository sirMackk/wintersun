from xml.dom.minidom import Document


class Feed:
    def __init__(self, feed_title, site_url, ts):
        self.doc = None
        self.feed = None
        self.entry_data = []
        self.settings = self._build_settings_list(feed_title, site_url, ts)
        self.create_feed()

    def _build_settings_list(self, title, url, timestamp):
        return [
            {'name': 'title',
             'value': title},
            {'name': 'link',
                'attributes': {
                    'rel': 'self',
                    'href': url + '/'}},
            {'name': 'link',
                'attributes': {
                    'rel': 'alternate',
                    'href': url}},
            {'name': 'id',
                'value': url + '/'},
            {'name': 'updated',
                'value': timestamp}]

    def create_header_nodes(self, doc):
        for setting in self.settings:
            el = doc.createElement(setting['name'])

            if 'value' in setting:
                el.appendChild(doc.createTextNode(setting['value']))

            if 'attributes' in setting:
                for k, v in setting['attributes'].items():
                    el.setAttribute(k, v)

            yield el

    def create_feed(self):
        """Creates Atom root element; Creates feed element"""
        doc = Document()
        feed = doc.createElement('feed')
        feed.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
        doc.appendChild(feed)

        for setting_node in self.create_header_nodes(doc):
            feed.appendChild(setting_node)

        self.doc = doc
        self.feed = feed

    def add_entry(self, entry):
        self.entry_data.append(entry)

    def generate_entry(self, entry_dict):
        # make into map + loop
        entry = self.doc.createElement('entry')

        title = self.doc.createElement('title')
        title.appendChild(self.doc.createTextNode(entry_dict['title']))

        link = self.doc.createElement('link')
        link.setAttribute('rel', 'alternate')
        link.setAttribute('type', 'text/html')
        link.setAttribute('href', entry_dict['link'])

        entry_id = self.doc.createElement('id')
        entry_id.appendChild(self.doc.createTextNode(entry_dict['link']))

        published = self.doc.createElement('published')
        published.appendChild(self.doc.createTextNode(entry_dict['published']))

        updated = self.doc.createElement('updated')
        updated.appendChild(self.doc.createTextNode(entry_dict['updated']))

        name = self.doc.createElement('name')
        name.appendChild(self.doc.createTextNode(entry_dict['name']))

        author = self.doc.createElement('author')
        author.appendChild(name)

        content = self.doc.createElement('content')
        content.setAttribute('type', 'html')
        content.appendChild(self.doc.createTextNode(entry_dict['content']))

        entry.appendChild(title)
        entry.appendChild(link)
        entry.appendChild(entry_id)
        entry.appendChild(published)
        entry.appendChild(updated)
        entry.appendChild(author)
        entry.appendChild(content)

        self.feed.appendChild(entry)

    def generate_xml(self, mAx=10):
        self.entry_data.sort(
            key=lambda entry: entry['published'], reverse=True)
        for entry in self.entry_data[:mAx]:
            self.generate_entry(entry)

        return self.doc.toprettyxml()
