'''
# small script to extract routes from a flask app
# and dislay it as a tree
'''
from __future__ import annotations
import importlib
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
from icecream import ic
from html import escape
from flask import Flask
from typing import cast, TypedDict, Optional

class EndpointData(TypedDict):
    url: str
    methods: set[str]|None
    endpoint: str

class TreeNode(TypedDict):
    children: dict[str, 'TreeNode']
    endpoint: Optional[EndpointData]

spacing_y = 100
spacing_x = 30
_id=1
def id()-> str:
    global _id
    _id += 1
    return str(_id)

class Node:
    _width = 140
    _height = 50
    def __init__(self, name: str, data: EndpointData|None):
        self.name = name
        self.endpoint = data['endpoint'] if data else None
        self.methods = data['methods'] if data else None
        self.children:list[Node] = []

    def add_child(self, child:Node)->None:
        self.children.append(child)

    @property
    def width(self)->float:
        if len(self.children)==0:
            return self._width
        return sum([child.width for child in self.children]) + (len(self.children)-1)*spacing_x


# Step 1: Import Flask app
def import_flask_app(module_name:str="app", app_name:str="app")->Flask:
    mod = importlib.import_module(module_name)
    return cast(Flask, getattr(mod, app_name))

# Step 2: Get route list
def get_routes(app: Flask)->list[EndpointData]:
    routes = []
    for rule in app.url_map.iter_rules():
        if "static" in rule.endpoint or "<lang>" in str(rule) or rule.subdomain=="dev":
            continue
        routes.append(EndpointData(url=str(rule), endpoint=rule.endpoint, methods=rule.methods))
    return routes

# Step 3: Build route tree
def insert_route(tree:dict[str,TreeNode], parts:list[str], route:EndpointData)->None:
    if not parts:
        return

    head, *tail = parts
    if head not in tree:
        tree[head] = {'children': {}, 'endpoint': None}

    if not tail:
        # Feuille : c’est un vrai endpoint
        tree[head]['endpoint'] = route
    else:
        insert_route(tree[head]['children'], tail, route)

def build_tree(routes: list[EndpointData])->dict[str, TreeNode]:
    tree:dict[str, TreeNode] = {}
    for route in routes:
        url:str = route['url']
        parts = [part for part in url.strip('/').split('/') if part]
        insert_route(tree, parts, route)
    return tree

def convert_tree(tree:dict[str, TreeNode])->list[Node]:
    out_tree = []
    for key, value in tree.items():
        n = Node(key, value['endpoint'])
        for child in convert_tree(value['children']):
            n.add_child(child)
        out_tree.append(n)
    return out_tree

# Step 4: Render tree as draw.io-compatible XML
def render_tree_xml(tree:list[Node], parent_element:Element, parent_id:str="root", x: float=0, y: float=0)->None:
    #ic(tree)
    for node in tree:
        if node.name == '':
            continue
        ic(node.width, node.name, [n.name for n in node.children], x, y)
        node_id = id()
        size = 8
        value = f'<font style="font-size: {size}px;">{node.endpoint}<br></font>{escape(node.name)}' if node.endpoint else escape(node.name)

        cell = SubElement(parent_element, 'mxCell', id=node_id, value=value,
                          style="shape=rectangle;whiteSpace=wrap;html=1;",
                          vertex="1")
        cell.set('parent', "1")
        geo = SubElement(cell, 'mxGeometry', x=str(x+(node.width+node._width)/2), y=str(y),
                         width=str(node._width), height=str(Node._height))
        geo.set('as', 'geometry')

        if parent_id != "root":
            '''
                <mxCell id="7" style="edgeStyle=none;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;exitX=0.5;exitY=1;exitDx=0;exitDy=0;" edge="1" parent="1" source="5" target="2">
                    <mxGeometry relative="1" as="geometry"/>
                </mxCell>
            '''
            arrow = SubElement(parent_element, 'mxCell', style="edgeStyle=none;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;exitX=0.5;exitY=1;exitDx=0;exitDy=0;shape=flexArrow;", 
                       edge="1", source=parent_id, target=node_id)
            arrow.set('parent', "1")
            geo = SubElement(arrow, 'mxGeometry', relative="1")
            geo.set('as', 'geometry')

        # Recursively draw children
        render_tree_xml(node.children, parent_element, node_id, x, y + node._height + spacing_y)
        x += node.width + spacing_x

# Step 5: Generate XML
def generate_drawio_tree(tree: list[Node], app: Flask)->str:
    mxfile = Element('mxfile', host="app.diagrams.net")
    diagram = SubElement(mxfile, 'diagram', name="Route Tree")
    model = SubElement(diagram, 'mxGraphModel')
    root = SubElement(model, 'root')

    SubElement(root, 'mxCell', id="0")
    SubElement(root, 'mxCell', id="1").set('parent', "0")

    base_node = Node(app.config['SERVER_NAME'], None)
    base_node.children = tree
    render_tree_xml([base_node], root)
    #ic(mxfile)
    xml_str = tostring(mxfile, encoding="utf-8")
    return parseString(xml_str).toprettyxml()

# Step 6: Main runner
if __name__ == "__main__":
    app = import_flask_app(module_name="chrono_des_vignes", app_name="app")
    routes = get_routes(app)
    tree = build_tree(routes)
    #ic(tree)
    out = convert_tree(tree)
    #ic(out)
    #ic(sum([n.width for n in out]))
    xml = generate_drawio_tree(out, app)

    with open("route_tree.drawio", "w", encoding="utf-8") as f:
        f.write(xml)

    print("✅ Route tree exported to route_tree.drawio")
