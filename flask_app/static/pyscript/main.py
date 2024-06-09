from pyscript import document
from pyodide.ffi.wrappers import add_event_listener
from html.parser import HTMLParser
import json

class Tag:
    _tag = None
    def _set_tag(self, tag):
        self._tag = str(tag)
    def _get_tag(self):
        return self._tag
    tag = property(_get_tag, _set_tag)

    _id = None
    def _set_id(self, id):
        self._id = str(id)
    def _get_id(self):
        return self._id
    id = property(_get_id, _set_id)

    _class = None
    def _set_class(self, class_):
        self._class = list(class_)
    def _get_class(self):
        return self._class
    Class = property(_get_class, _set_class)

    _style = None
    def _set_style(self, style):
        self._style = dict(style)
    def _get_style(self):
        return self._style
    style = property(_get_style, _set_style)

    _attrs = None
    def _set_attrs(self, attrs):
        self._attrs = dict(attrs)
    def _get_attrs(self):
        return self._attrs
    attrs = property(_get_attrs, _set_attrs)

    _parent = None
    def _set_parent(self, parent):
        self._parent = parent
    def _get_parent(self):
        return self._parent
    parent = property(_get_parent, _set_parent)

    _childs = None
    def _set_childs(self, childs):
        self._childs = list(childs)
    def _get_childs(self):
        return self._childs
    childs = property(_get_childs, _set_childs)

    def __init__(self, html_modif, tag, id, class_, style, attrs, parent=None, childs=None, html_element=None):
        self.html_modif = html_modif
        self.tag = tag
        self.id = id
        self.Class = class_
        self.style = style
        self.attrs = attrs
        self.parent:Tag = parent
        self.childs = childs if childs else []
        self.html_element=html_element if html_element else None

    def on_click(self, event):
        if event.target != self.html_element:
            return
        elif self.html_modif.modified_tag == self:
            return
        print('click', self.id)
        self.html_modif.clear_modif()
        self.html_element.className += ' border-danger '
        self.html_modif.set_modif(self)

    def out_click(self, event=None):
        print('un click', self.id)
        self.html_element.className = f"{' '.join(self.Class)} border"

    def get_modif_html(self):
        html = f'<{self.tag} id="{self.id}" class="{' '.join(self.Class)} border" style="{'; '.join([f'{k}:{v}' for k,v in self.style.items()])}" {' '.join([f'{k}="{v}"' for k,v in self.attrs.items()])} >'
        for element in self.childs:
            if isinstance(element, str):
                html += element
            elif isinstance(element, Tag):
                html += element.get_modif_html()
        html += f'</{self.tag}>'

        return html

    def load_html_element(self, document):
        self.html_element = document.getElementById(self.id)
        add_event_listener(self.html_element, 'click', self.on_click)

        for element in self.childs:
            if isinstance(element, Tag):
                element.load_html_element(document)

    def add_child(self, data):
        self.childs.append(data)

class JinjaExpretionTag(Tag):
    def __init__(self, html_modif, full_tag, id, class_, style, attrs, parent=None, childs=None, html_element=None):
        self.html_modif = html_modif
        self.tag = full_tag.strip()[2:-2].strip()
        self.id = id
        self.Class = class_
        self.style = style
        self.attrs = attrs
        self.parent:Tag = parent
        self.childs = childs if childs else []
        self.html_element=html_element if html_element else None

class JinjaCodeTag(Tag):
    def __init__(self, html_modif, full_tag, id, class_, style, attrs, parent=None, childs=None, html_element=None):
        self.html_modif = html_modif
        self.type = full_tag.strip()[2:-2].strip().split(" ")[0]
        self.tag = full_tag.strip()[2:-2].strip()
        self.id = id
        self.Class = class_
        self.style = style
        self.attrs = attrs
        self.parent:Tag = parent
        self.childs = childs if childs else []
        self.html_element=html_element if html_element else None

class HTML_modif:
    def __init__(self, modif_div):
        self.modified_tag = None
        self.modif_div = modif_div

    _options = ['div', 'p', 'h1', 'h2', 'h3', 'ul', 'li', 'img']

    def set_modif(self, tag):
        self.modified_tag = tag
        self.modif_div.innerHTML = self.get_modif_form()
        options = document.getElementById('dossard_form_tag').getElementsByTagName('option')
        options[self._options.index(self.modified_tag.tag)].selected = 'selected'

    def clear_modif(self):
        if self.modified_tag:
            self.modified_tag.out_click()
            self.modified_tag = None
            self.modif_div.innerHTML = ''

    def get_modif_form(self):
        html = \
            '''<form id="dossard_modif_form">
                <fieldset>
                    <label for="tag">type</label><br>
                    <select name="tag" id="dossard_form_tag">
                        <option value="div">groupe</option>
                        <option value="p">text</option>
                        <option value="h1">titre 1</option>
                        <option value="h2">titre 2</option>
                        <option value="h3">titre 3</option>
                        <option value="ul">list</option>
                        <option value="li">list element</option>
                        <option value="img">image</option>
                    </select>
                </fieldset>
            </form>'''
        return html

class MyHTMLParser(HTMLParser):
    def __init__(self, html_modif):
        self.html_modif = html_modif
        super().__init__()

    def get_attr(self,attrs, name):
        for n,v in attrs:
            if n==name:
                return v

    def attr_dict(self,attrs):
       rattrs={}
       rclass=[]
       rstyle={}
       for k,v in attrs:
            if k=="style":
                rstyle = {all.strip().split(':')[0]:all.strip().split(':')[1] for all in v.split(';')}
            elif k=="class":
                rclass = [c.strip() for c in v.split(' ')]
            else:
                rattrs[k] = v
       return rstyle, rclass, rattrs


    id_num =0x0
    parents:list[Tag|str]=[]
    master = None
    ids={}
    def id(self, attrs):
        id = self.get_attr(attrs, 'id')
        if id:
            id = 'user:'+ id
        else:
            self.id_num +=0x1
            id = 'code:'+ str(self.id_num)
        return id

    def handle_jinja_tag(self, data):
        code_i = data.find('{%')
        var_i = data.find('{{')
        if max(code_i, var_i) == -1:
            return False
        first = min(code_i, var_i)
        close = '}}' if var_i < code_i else '%}'
        if first == 0:
            pass
        else:
            self.handle_data(data[:first])
            data = data[first:]
            end = data.find(close)
            if end == -1:
                raise Exception()
            



    def handle_starttag(self, tag, attrs):
        id = self.id(attrs)
        rstyle, rclass, rattrs = self.attr_dict(attrs)
        tag = Tag(self.html_modif, tag, id, rclass, rstyle, rattrs, self.parents[-1] if len(self.parents)>0 else None)
        if len(self.parents)>0:
            self.parents[-1].add_child(tag)
        self.parents.append(tag)
        if self.master is None:
            self.master = tag
        self.ids[id] = tag

    def handle_endtag(self, tag):
        del self.parents[-1]

    def handle_data(self, data):
        if not self.handle_jinja_tag(data):
            if len(self.parents)>0:
                self.parents[-1].add_child(data)

html = '<html><head><title>Test</title></head><body class="black"><h1 id="d">Parse me!</h1><p>coucou</p></body></html>'
html ='''
<div>
<h2 id="coucou">HTML Images</h2>
<p>HTML images are defined with the img tag:</p>

<img src="/static/favicon.ico" alt="logo" width="104">
</div>
'''

html =   '''<h1>{{ test_name }} Results</h1>
            <ul>
            {% for student in students %}
                <li>
                    <p>{{ student.name }}:</p> {{ student.score }}/{{ max_score }}
                </li>
            {% endfor %}
            </ul>'''

def load_html():
    html_modif = HTML_modif(dossard_modif)
    parser = MyHTMLParser(html_modif)
    parser.feed('<div>'+html+'</div>')
    master = parser.master
    parser.close()
    print(dossard_content.innerHTML)
    dossard_content.innerHTML = master.get_modif_html()
    master.load_html_element(document)


dossard_modif = document.getElementById('dossard_modif')
dossard_content = document.getElementById('dossard_content')
load_html()