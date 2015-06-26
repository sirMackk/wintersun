from xml.dom.minidom import Document


class Feed(object):
    def __init__(self, settings):
        self.settings = settings
        self.create_feed()

    def create_header_nodes(self, doc):
        for setting in self.settings:
            el = doc.createElement(setting['name'])

            if 'value' in setting:
                el.appendChild(doc.createTextNode(setting['value']))

            if 'attributes' in setting:
                for k, v in setting['attributes'].iteritems():
                    el.setAttribute(k, v)

            yield el



    def create_feed(self):
        doc = Document()
        feed = doc.createElement('feed')
        feed.setAttribute('xmlns', 'http://www.w3.org/2005/Atom')
        doc.appendChild(feed)

        for setting_node in self.create_header_nodes(doc):
            feed.appendChild(setting_node)

        self.doc = doc
        self.feed = feed

    def add_entry(self, entry):
        # make into map + loop
        entry = self.doc.createElement('entry')

        title = self.doc.createElement('title')
        title.appendChild(self.doc.createTextNode(entry['title']))

        link = self.doc.createElement('link')
        link.setAttribute('rel', 'alternate')
        link.setAttribute('type', 'text/html')
        link.setAttribute('href', entry['link'])

        entry_id = self.doc.createElement('id')
        entry_id.appendChild(self.doc.createTextNode(entry['link']))

        published = self.doc.createElement('published')
        published.appendChild(self.doc.createTextNode(entry['published']))

        updated = self.doc.createElement('updated')
        updated.appendChild(self.doc.createTextNode(entry['updated']))

        name = self.doc.createElement('name')
        name.appendChild(self.doc.createTextNode(entry['name']))

        author = self.doc.createElement('author')
        author.appendChild(name)

        content = self.doc.createElement('content')
        content.setAttribute('type', 'xhtml')
        content.appendChild(self.doc.createTextNode(entry['content']))

        entry.appendChild(title)
        entry.appendChild(link)
        entry.appendChild(entry_id)
        entry.appendChild(published)
        entry.appendChild(updated)
        entry.appendChild(author)
        entry.appendChild(content)

        self.feed.appendChild(entry)

    def generate_xml(self):
        return self.doc.toprettyxml()
