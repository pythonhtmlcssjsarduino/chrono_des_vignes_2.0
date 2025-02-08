from pyscript import document
from pyodide.ffi.wrappers import add_event_listener
from jinja2 import Environment
from html.parser import HTMLParser
import json

class Tag:
    def __init__(self, html_modif, tag, id, class_, style, attrs, parent=None, childs=None, html_element=None):
        self.html_modif = html_modif
        self.tag = tag
        self.id = id
        self.Class = class_
        self.style:dict = style
        self.attrs = attrs
        self.parent:Tag = parent
        self.childs = childs if childs else []
        self.html_element=html_element if html_element else None

    def __str__(self) -> str:
        return f'<Tag tag:{self.tag} id:{self.id} >'
    
    def __repr__(self) -> str:
        return str(self)

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
            else:
                html += element.get_modif_html()
        html += f'</{self.tag}>'

        return html

    def get_output_html(self):
        html = f'<{self.tag}'
        html += f' id="{self.id[5:]}"' if self.id.startswith('user:') else ''
        html += f' class="{' '.join(self.Class)}"' if len(self.Class)>0 else ''
        html += f' style="{'; '.join([f'{k}:{v}' for k,v in self.style.items()])}"' if len(self.style)>0 else ''
        html += f' {' '.join([f'{k}="{v}"' for k,v in self.attrs.items()])} >'
        for element in self.childs:
            if isinstance(element, str):
                html += element
            else:
                html += element.get_output_html()
        html += f'</{self.tag}>'

        return html

    def change_style(self, event, js_attr, css_attr, value):
        if event.target.checked:
            if self.style.get(css_attr):
                self.style[css_attr] += ' '+value
            else:
                self.style[css_attr] = value
            exec(f'self.html_element.style.{js_attr} = self.style[css_attr]')
        else:
            if self.style.get(css_attr):
                self.style[css_attr] = self.style[css_attr].replace(value, '').strip()
                exec(f'self.html_element.style.{js_attr} = self.style[css_attr]')
        self.html_modif.update_preview()

    def change_color(self, e):
        self.style['color'] = e.target.value
        self.html_element.style.color = self.style['color']
        self.html_modif.update_preview()

    def change_select_style(self, e, js_attr, css_attr):
        self.style[css_attr] = e.target.value
        exec(f'self.html_element.style.{js_attr} = self.style[css_attr]')
        self.html_modif.update_preview()

    def set_modif(self, modif_form):
        if self.tag in ('p', 'h1', 'h2', 'h3', 'li'):
            blocks = modif_form.getElementsByTagName('fieldset')
            # les propriété avec des checkbox
            style = blocks[0].getElementsByTagName('input')
            for i, ((css_p, js_p), val) in enumerate(((('font-style', 'fontStyle'), 'italic'), (('font-weight', 'fontWeight'), 'bold'), (('text-decoration-line', 'textDecorationLine'), 'underline'), (('text-decoration-line', 'textDecorationLine'), 'line-through'))) :
                style[i].checked = val in self.style.get(css_p, '')
                add_event_listener(style[i], 'change', lambda e, ja=js_p, ca = css_p, v=val:self.change_style(e, ja, ca, v) )

            # color
            color = blocks[1].getElementsByTagName('input')[0]
            color.value = self.style.get('color', 'black')
            add_event_listener(color, 'change', self.change_color)


            text_pos = blocks[1].getElementsByTagName('select')
            align = text_pos[0].getElementsByTagName('option')
            align[['left', 'center', 'right'].index(self.style.get('text-align', 'center'))].selected = 'selected'
            add_event_listener(text_pos[0], 'change', lambda e, ja='textAlign', ca ='text-align':self.change_select_style(e, ja, ca))

            align = text_pos[1].getElementsByTagName('option')
            align[self.style.get('text-align', 'center')+1].selected = 'selected'
            add_event_listener(text_pos[1], 'change', lambda e, ja='fontSize', ca ='font-size':self.change_select_style(e, ja, ca))

    def load_html_element(self, document):
        self.html_element = document.getElementById(self.id)
        add_event_listener(self.html_element, 'click', self.on_click)

        for element in self.childs:
            if not isinstance(element, str):
                element.load_html_element(document)

    def add_child(self, data):
        self.childs.append(data)
class JinjaExpressionTag:
    def __init__(self, html_modif, id, var_name, parent=None, childs=None, html_element=None):
        self.html_modif = html_modif
        self.id = id
        self.var = var_name
        self.parent:Tag = parent
        self.html_element=html_element if html_element else None

    def load_html_element(self, document):
        self.html_element = document.getElementById(self.id)
        add_event_listener(self.html_element, 'click', self.on_click)

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
        self.html_element.className = f"border"

    def get_modif_html(self):
        html = f'<p id="{self.id}" class="border" >[[{self.var}]]</p>'

        return html

    def get_output_html(self):
        html = '{{ ' + f'{self.var}' + ' }}'

        return html

    def __str__(self):
        return f'<JinjaExpressionTag var:{self.var} >'

class JinjaForTag:
    def __init__(self, html_modif, id, in_vars, out_var, parent=None, childs=None, html_element=None):
        self.html_modif = html_modif
        self.id = id
        self.in_vars = in_vars
        self.out_var = out_var
        self.parent:Tag = parent
        self.childs = childs if childs else []
        self.html_element=html_element if html_element else None

    def get_modif_html(self):
        html = f'<div id="{self.id}" class="border" >[~ pour {', '.join(self.in_vars)} dans {self.out_var} ~]'
        for element in self.childs:
            if isinstance(element, str):
                html += element
            else:
                html += element.get_modif_html()
        html += f'</div>'

        return html

    def get_output_html(self):
        #end = '.items()' if self.out_var
        html = '{% ' + f'for {', '.join(self.in_vars)} in {self.out_var}' + ' %}'
        for element in self.childs:
            if isinstance(element, str):
                html += element
            else:
                html += element.get_output_html()
        html += '{% endfor %}'

        return html

    def add_child(self, data):
        self.childs.append(data)

    def load_html_element(self, document):
        self.html_element = document.getElementById(self.id)
        add_event_listener(self.html_element, 'click', self.on_click)

        for element in self.childs:
            if not isinstance(element, str):
                element.load_html_element(document)

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
        self.html_element.className = f"border"

    def __str__(self):
        return f'<JinjaForTag for {self.in_vars} in {self.out_var} >'

class HTML_modif:
    def __init__(self, modif_div, output_div, vars, test_data):
        self.modified_tag = None
        self.modif_div = modif_div
        self.output_div = output_div
        self.childs = []
        self.vars =vars
        self.test_data =test_data
        self.env = Environment()

    def get_modif_html(self):
        html = '<style>#dossard_content p {display:inline}</style>'
        for element in self.childs:
            if isinstance(element, str):
                html += element
            else:
                html += element.get_modif_html()

        return html

    def load_html_element(self, document):
        for element in self.childs:
            if not isinstance(element, str):
                element.load_html_element(document)

    def add_child(self, data):
        self.childs.append(data)

    _options = ['div', 'p', 'h1', 'h2', 'h3', 'ul', 'li', 'img', 'jinja_var', 'jinja_for']

    def set_modif(self, tag):
        self.modified_tag = tag
        self.modif_div.innerHTML = self.get_modif_form()
        options = document.getElementById('dossard_form_tag').getElementsByTagName('option')
        if isinstance(tag, Tag):
            options[self._options.index(self.modified_tag.tag)].selected = 'selected'
        elif isinstance(tag, JinjaExpressionTag):
            options[self._options.index('jinja_var')].selected = 'selected'
        elif isinstance(tag, JinjaForTag):
            options[self._options.index('jinja_for')].selected = 'selected'
        modif_form = document.getElementById("custum_modif")
        self.modified_tag.set_modif(modif_form)

    def clear_modif(self):
        if self.modified_tag:
            self.modified_tag.out_click()
            self.modified_tag = None
            self.modif_div.innerHTML = ''

    def get_modif_form(self):
        style = ''' <label>style</label><br>
                    <input type="checkbox" name="italic">italic</input></br>
                    <input type="checkbox" name="bold">gras</input></br>
                    <input type="checkbox" name="underline">souligné</input></br>
                    <input type="checkbox" name="through">tracé</input></br>'''
        text_aspect = '''<label>couleur</label><br>
                        <input type="color" name="color"></br>
                        <label for="align" >alignement</label><br>
                        <select name="align">
                            <option value="left">gauche</option>
                            <option value="center">centré</option>
                            <option value="right">droite</option>
                        </select><br>
                        <label for="size" >taille</label><br>
                        <select name="size">
                            <option value="1">1</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                            <option value="4">4</option>
                            <option value="5">5</option>
                            <option value="6">6</option>
                        </select><br>'''
        border_type = '''   <label for="border_type" >type de bordure</label><br>
                            <select name="border_type">
                                <option value="none">none</option>
                                <option value="dotted">dotted</option>
                                <option value="dashed">dashed</option>
                                <option value="solid">solid</option>
                                <option value="double">double</option>
                                <option value="groove">groove</option>
                                <option value="ridge">ridge</option>
                                <option value="inset">inset</option>
                                <option value="outset">outset</option>
                            </select><br>'''
        if isinstance(self.modified_tag, Tag):
            if self.modified_tag.tag in ('p', 'h1', 'h2', 'h3', 'li'):
                spec = f''' <fieldset>
                                {style}
                            </fieldset>
                            <div class="vr"></div>
                            <fieldset>
                                {text_aspect}
                            </fieldset>'''
            elif self.modified_tag.tag in ('ul', 'ol'):
                types = (('circle', 'rond'), ('square', 'carré')) if self.modified_tag.tag == 'ul' else (('roman', 'chiffres romain'), ('alpha', 'chiffres latin'))
                spec = f''' <fieldset>
                                {style}
                                <input type="checkbox" name="display">afficher les puces</input></br>
                            </fieldset>
                            <div class="vr"></div>
                            <fieldset>
                                <label for="type" >type</label><br>
                                <select name="type">
                                    <option value="{types[0][0]}">{types[0][1]}</option>
                                    <option value="{types[1][0]}">{types[1][1]}</option>
                                </select><br>
                            </fieldset>'''
            elif self.modified_tag.tag == 'img':
                spec = f''' <fieldset>
                                <input type="file" name="file"></input></br>
                                <fieldset class="d-flex justify-content-around">
                                    <fieldset>
                                        <label for="border_width" >largeur de la bordure</label><br>
                                        <select name="border_width">
                                            <option value="1">1</option>
                                            <option value="2">2</option>
                                            <option value="3">3</option>
                                            <option value="4">4</option>
                                            <option value="5">5</option>
                                            <option value="6">6</option>
                                        </select><br>
                                    </fieldset>
                                    <div class="vr"></div>
                                    <fieldset>
                                        <label for="radius" >rayon des coins</label><br>
                                        <select name="radius">
                                            <option value="1">1</option>
                                            <option value="2">2</option>
                                            <option value="3">3</option>
                                            <option value="4">4</option>
                                            <option value="5">5</option>
                                            <option value="6">6</option>
                                        </select><br>
                                        {border_type}
                                    </fieldset>
                                </fieldset>
                            </fieldset>'''
        elif isinstance(self.modified_tag, JinjaExpressionTag):
            pass

        html = \
            f'''<form id="dossard_modif_form" class="d-flex justify-content-around">
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
                        <option value="jinja_var">jinja var</option>
                        <option value="jinja_for">jinja for loop</option>
                    </select>
                </fieldset>
                <div class="vr"></div>
                <fieldset id="custum_modif" class="d-flex justify-content-around">{spec}</fieldset>
            </form>'''
        return html

    def get_jinja_vars(self):
        '''
        custum_name:{   #*nothing if just a var
                        'list':{    #* names of the atrributes of the items inside with same full sintaxe
                        }
                        'dict':{    #* names of the dict items 
                        }
        }
        '''
        return self.vars
    
    def get_output_html(self):
        html = '<style>#output_content p {display:inline}</style>'
        for element in self.childs:
            if isinstance(element, str):
                html += element
            else:
                html += element.get_output_html()

        return html
    

    def update_preview(self):
        template = self.env.from_string(self.get_output_html())
        output = template.render(self.test_data)
        self.output_div.innerHTML = output

class MyHTMLParser(HTMLParser):

    id_num =0x0
    parents:list[Tag|str]=[]
    ids={}
    def __init__(self, html_modif):
        self.html_modif = html_modif
        self.parents.append(self.html_modif)
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

    def id(self, attrs={}):
        id = self.get_attr(attrs, 'id')
        if id:
            id = 'user:'+ id
        else:
            self.id_num +=0x1
            id = 'code:'+ str(self.id_num)
        return id

    def handle_jinja_data(self, data):
        if len (data) == 0:
            return
        code_i = data.find('{%')
        var_i = data.find('{{')
        if max(code_i, var_i) == -1:
            print('simple_data', f'"{data}"')
            self.handle_simple_data(data)
            return
        var_i = var_i if var_i >=0 else len(data)
        code_i = code_i if code_i >=0 else len(data)
        first = min(code_i, var_i)
        close = '}}' if var_i < code_i else '%}'
        if first != 0:
            self.handle_simple_data(data[:first])
        data = data[first+2:]
        end = data.find(close)
        if end == -1:
            raise Exception()
        if var_i < code_i:
            # ajouter la var dans le parent
            var = JinjaExpressionTag(self.html_modif, self.id(), data[:end].strip(), self.parents[-1])
            self.parents[-1].add_child(var)
        elif data[:end].strip().startswith("end"):
            self.handle_endtag()
        else:
            args = [e for e in data[:end].strip().split(' ') if len(e.strip()) > 0]
            type = args[0]
            if type == 'for':
                vars = data[:end].replace('for', '').split('in')
                out = vars[1].strip()
                ins = [e.strip() for e in vars[0].split(',')]
                code = JinjaForTag(self.html_modif, self.id(), ins, out, self.parents[-1])
                self.parents[-1].add_child(code)
                self.parents.append(code)
            else:
                raise NotImplementedError()
        if len( data[end+2:].strip()) > 0:
            self.handle_jinja_data(data[end+2:])

    def handle_simple_data(self, data):
        self.parents[-1].add_child(data)

    def handle_starttag(self, tag, attrs):
        id = self.id(attrs)
        rstyle, rclass, rattrs = self.attr_dict(attrs)
        tag = Tag(self.html_modif, tag, id, rclass, rstyle, rattrs, self.parents[-1] if len(self.parents)>0 else None)
        self.parents[-1].add_child(tag)
        self.parents.append(tag)
        self.ids[id] = tag

    def handle_endtag(self, tag=None):
        del self.parents[-1]

    def handle_data(self, data):
        self.handle_jinja_data(data)

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
            </ul>
            <img src="/static/favicon.ico" alt="logo" width="104">'''

html_test_var_sintaxe = {'test_name':{}, 'students':{'list':{'name':{}, 'score':{}}}, 'max_score':{}}

html_test_dataset = {'test_name':'test #1', 'max_score':'50', 'students':[{'name':'romain', 'score':'40'}, {'name':'un autre', 'score':'27'}, {'name':'un dernier', 'score':'2,7'}]}

def load_html():
    html_modif = HTML_modif(dossard_modif, output_content, html_test_var_sintaxe, html_test_dataset)
    parser = MyHTMLParser(html_modif)
    parser.feed(html)
    master = parser.parents[0]
    parser.close()
    dossard_content.innerHTML = master.get_modif_html()
    master.update_preview()
    master.load_html_element(document)


dossard_modif = document.getElementById('dossard_modif')
dossard_content = document.getElementById('dossard_content')
output_content = document.getElementById('output_content')
load_html()