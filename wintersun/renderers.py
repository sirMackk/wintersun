from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    def __init__(self, template_dir):
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir))

    def render(self, template_name, **kwargs):
        template = self.template_env.get_template(template_name)
        return template.render(**kwargs)
