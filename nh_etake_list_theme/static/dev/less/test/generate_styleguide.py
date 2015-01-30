__author__ = 'colin'
import pykss
from jinja2 import Template

styleguide = pykss.Parser('css/files/')
tmpl = open('styleguide_template.html', 'r').read()
template = Template(tmpl)
styleguide_render = template.render(sections=sorted(styleguide.sections.items()),
                                    nav_sections=sorted(styleguide.sections.items()),
                                    css_sections=sorted(styleguide.sections.items()))
styleguide_file = open('styleguide.html', 'w')
styleguide_file.write(styleguide_render)
styleguide_file.close()