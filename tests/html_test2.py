import os
from pyhtml2pdf import converter

path = os.path.abspath('test.html')
converter.convert(f'file:///{path}', 'sample.pdf')