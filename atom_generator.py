from datetime import datetime
from xml.dom.minidom import Document

import pytz


def create_timestamp(date=None):
    if date:
        return date + 'T00:00:00+01:00'
    else:
        localtz = pytz.timezone("Europe/Berlin")
        return datetime.now().replace(tzinfo=localtz).strftime(
            "%Y-%m-%dT%H:%M:%S+01:00")


class Feed(object):
    # add entry should add item to list,
    # then sort by something before generating xml
    def __init__(self, settings):
        self.entry_data = []
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
