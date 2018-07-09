import pytest

from wintersun import renderers


@pytest.fixture()
def template_dir(tmpdir):
    template_dir = tmpdir.mkdir('templates')
    index_template = template_dir.join('index.html')
    post_template = template_dir.join('post.html')

    index_template.write('<h1>Index</h1>'
                         '{% for page in pages %}'
                         '{{ page.title }}'
                         '{% endfor %}')

    post_template.write('<h1>{{ title }}</h1>'
                        '<h2>{{ date }}</h2>'
                        '{{ contents }}')
    return template_dir


@pytest.fixture
def renderer(template_dir):
    return renderers.TemplateRenderer(template_dir.strpath)


class TestTemplateRenderer:
    @pytest.mark.integration
    def test_render_sample_page(self, renderer):
        parts = {
            'title': 'Page title',
            'date': '2018-01-06 10:52:32',
            'contents': 'Lorem ipsum'
        }
        res = renderer.render('post.html', **parts)

        assert res == (f'<h1>{parts["title"]}</h1><h2>{parts["date"]}</h2>'
                       f'{parts["contents"]}')
