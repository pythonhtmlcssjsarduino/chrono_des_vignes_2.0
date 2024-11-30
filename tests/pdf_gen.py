from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm
from reportlab.lib.pagesizes import A4, A0, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from math import floor

name = 'parcours 2'
data = [['place', 'nom', 'prénom', 'dossard', 'temps'],
           [1, 'toi', 'tu', 34, '0:00:00'],
           *[[i, 'aurelien', 'maurer', 32, '0:00:42'] for i in range(2, 50)]]
width, height = size = A4

filename = 'tests/pdf_test.pdf'
pdf = canvas.Canvas(filename, pagesize=portrait(size))
style = TableStyle([
            *[('BACKGROUND',(0,row),(-1,row), colors.skyblue if row%2==1 else colors.aqua) for row in range(len(data))],
            *[('LINEBELOW',(0,row),(-1,row), 0.5, colors.black) for row in range(len(data)-1)],
            ('BOX', (0,0), (-1,-1), 0.5, colors.black)
            ])
start = 4*cm
up_margin = 2*cm
down_margin = 2*cm
for page_data in [data]*2:
    # draw title
    pdf.setFontSize(1.5*cm)
    pdf.drawCentredString(width/2, height-2.5*cm, name)

    # draw table
    table = Table(data, style=style,
                colWidths=[.07*width,.20*width,.20*width,.10*width,.10*width]
                )
    w, h = table.wrapOn(pdf, 0, 0)
    row_height = h/len(page_data)
    cur_row = 0
    t_height = height-start-down_margin
    other_height = height-up_margin-down_margin
    m=start
    end= False
    while not end:
        delta_row = floor(t_height/row_height)
        if (delta_row==0):
            raise Exception('il \'y as pas assez de place')
        rows = page_data[cur_row:cur_row+delta_row]
        style = TableStyle([
            *[('BACKGROUND',(0,row),(-1,row), colors.skyblue if row%2==1 else colors.aqua) for row in range(len(rows))],
            *[('LINEBELOW',(0,row),(-1,row), 0.5, colors.black) for row in range(len(rows)-1)],
            ('BOX', (0,0), (-1,-1), 0.5, colors.black)
        ])
        table = Table(rows, style=style,
            colWidths=[.07*width,.20*width,.20*width,.10*width,.10*width]
            )
        w, h = table.wrapOn(pdf, 0, 0)
        table.drawOn(pdf, (width-w)/2, height-h-m)
        cur_row+=delta_row
        t_height=other_height
        m=up_margin
        pdf.showPage()
        if cur_row>=len(page_data):
            end=True

pdf.save()