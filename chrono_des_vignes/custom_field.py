from markupsafe import Markup
from wtforms import widgets, SelectMultipleField, StringField
from wtforms.widgets import Input

class BootstrapListWidget(widgets.ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li class='list-group-item'>{subfield.label} {subfield(class_='form-check-input ms-1')}</li>")
            else:
                html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))

class BootstrapListWidgetWithDescription(widgets.ListWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in field:
            try: data = eval(subfield.data)
            except: data = None
            if isinstance(data, tuple):
                if data[1]is None:
                    data=(data[0], '')
                if self.prefix_label:
                    html.append(f"<li class='list-group-item'>{subfield.label().replace(subfield.data, data[0])} {subfield(class_='form-check-input ms-1')}<p class='small'>{data[1]}</p></li>")
                else:
                    html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label().replace(subfield.data, data[0])}<p class='small'>{data[1]}</p></li>")
            else:
                if self.prefix_label:
                    html.append(f"<li class='list-group-item'>{subfield.label} {subfield(class_='form-check-input ms-1')}</li>")
                else:
                    html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
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

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]
        else:
            self.data = ''