'''
# Chrono Des Vignes
# a timing system for sports events
# 
# Copyright © 2024-2025 Romain Maurer
# This file is part of Chrono Des Vignes
# 
# Chrono Des Vignes is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# 
# Chrono Des Vignes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>.
# 
# You may contact me at chrono-des-vignes@ikmail.com
'''

from collections.abc import Iterable
from markupsafe import Markup
from wtforms import widgets, SelectMultipleField, StringField, Field
from wtforms.widgets import Input
from typing import Any, cast

class BootstrapListWidget(widgets.ListWidget):
    def __call__(self, field: Field, **kwargs: Any)->Markup:
        """
        Render a list of checkboxes.

        :param field: The field to render.
        :param kwargs: Additional keyword arguments to pass to the widget.
        :return: The rendered HTML.
        """
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in cast(Iterable[Field], cast(object, field)):
            if self.prefix_label:
                html.append(f"<li class='list-group-item'>{subfield.label} {subfield(class_='form-check-input ms-1')}</li>")
            else:
                html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))

class BootstrapListWidgetWithDescription(widgets.ListWidget):
    def __call__(self, field: Field, **kwargs: Any)->Markup:
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in cast(Iterable[Field], cast(object, field)):
            try: 
                data = eval(subfield.data)
            except (SyntaxError, TypeError): 
                data = None
            if isinstance(data, tuple):
                if data[1]is None:
                    data=(data[0], '')
                if self.prefix_label:
                    html.append(f"<li class='list-group-item'>{Markup(data[0])} {subfield(class_='form-check-input ms-1')}<p class='small'>{data[1]}</p></li>")
                else:
                    html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {Markup(data[0])}<p class='small'>{data[1]}</p></li>")
            else:
                if self.prefix_label:
                    html.append(f"<li class='list-group-item'>{subfield.label()} {subfield(class_='form-check-input ms-1')}</li>")
                else:
                    html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label()}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = BootstrapListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class MultiCheckboxFieldWithDescription(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.
    each objects need to be a string repr of a 2 element tuple like:
    --> str(('label', 'description'))

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = BootstrapListWidgetWithDescription(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ColorField(StringField):
    widget = Input(input_type='color')

    def process_formdata(self, valuelist:list[Any])->Any:
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = ''