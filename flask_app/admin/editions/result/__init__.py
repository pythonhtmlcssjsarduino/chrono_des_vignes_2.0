from flask import Blueprint, render_template, send_file, request
from flask_login import login_required, current_user
from flask_app import admin_required, db, set_route, lang_url_for as url_for
from flask_app.models import Event, Edition, Passage, PassageKey, Stand, Inscription
from sqlalchemy import and_
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from xlsxwriter import Workbook
from math import floor

result = Blueprint('result', __name__, template_folder='templates')

def get_result_data(edition, parcours):
    coureurs:list[Inscription] = Inscription.query.filter(Inscription.edition==edition, Inscription.parcours==parcours).all()
    fini = []
    non_fini = []
    for coureur in coureurs:
        if coureur.end is None:
            continue
        data = {'time':coureur.get_time(), 'name':coureur.inscrit.name, 'lastname':coureur.inscrit.lastname, 'dossard':coureur.dossard}
        if coureur.end == 'finish':
            fini.append(data)
        else:
            data['rank'] = {'abandon':'abandon', 'disqual':'disqualifié', 'absent':'absent'}[coureur.end]
            non_fini.append(data)
    fini = sorted(fini, key=lambda item:item['time'])
    for i, coureur in enumerate(fini):
        fini[i]['rank'] = i+1

    non_fini = sorted(non_fini, key=lambda item:{'abandon':1, 'disqualifié':2, 'absent':3}[item['rank']])
    return fini + non_fini 

def get_result_pdf(edition:Edition):
    buffer = BytesIO()
    width, height = size = A4

    pdf = canvas.Canvas(buffer, pagesize=portrait(size))
    start = 4*cm
    up_margin = 2*cm
    down_margin = 2*cm
    for parcours in edition.parcours:
        data = [['place', 'nom', 'prénom', 'dossard', 'temps']]
        for row in get_result_data(edition, parcours):
            data.append([row['rank'], row['name'], row['lastname'], row['dossard'], str(row['time'])])
        # draw title
        title = f'parcours : {parcours.name}'
        pdf.setFontSize(1.5*cm)
        pdf.drawCentredString(width/2, height-2.5*cm, title)

        # draw table
        style = TableStyle([
                *[('BACKGROUND',(0,row),(-1,row), colors.skyblue if row%2==1 else colors.aqua) for row in range(len(data))],
                *[('LINEBELOW',(0,row),(-1,row), 0.5, colors.black) for row in range(len(data)-1)],
                ('BOX', (0,0), (-1,-1), 0.5, colors.black)
                ])
        table = Table(data, style=style,
                    colWidths=[.07*width,.20*width,.20*width,.10*width,.10*width]
                    )
        w, h = table.wrapOn(pdf, 0, 0)
        row_height = h/len(data)
        cur_row = 0
        t_height = height-start-down_margin
        other_height = height-up_margin-down_margin
        m=start
        end= False
        while not end:
            delta_row = floor(t_height/row_height)
            if (delta_row==0):
                raise Exception('il \'y as pas assez de place')
            rows = data[cur_row:cur_row+delta_row]
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
            if cur_row>=len(data):
                end=True

    pdf.save()
    buffer.seek(0)
    return buffer

@set_route(result, '/event/<event_name>/editions/<edition_name>/result_pdf')
@login_required
@admin_required
def pdf_result(event_name, edition_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    return send_file(get_result_pdf(edition), download_name='result.pdf', as_attachment=request.args.get('download', False))

def get_result_excel(edition:Edition):
    buffer = BytesIO()

    workbook = Workbook(buffer)
    for parcours in edition.parcours:
        data = get_result_data(edition, parcours)
        ic(data)
        worksheet = workbook.add_worksheet()
        for y, rows in enumerate(data, start=1):
            ic(y)
            for x, cell in enumerate(['rank', 'name', 'lastname', 'dossard', 'time']):
                ic(x)
                worksheet.write(y, x, rows[cell])
        worksheet.add_table(0,0,max(len(data), 1),4, {'columns': [{'header': h} for h in ['place', 'nom', 'prénom', 'dossard', 'temps']], 'autofilter': False})
    workbook.close()

    buffer.seek(0)
    return buffer

@set_route(result, '/event/<event_name>/editions/<edition_name>/result_xlsx')
@login_required
@admin_required
def xlsx_result(event_name, edition_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    return send_file(get_result_excel(edition), download_name='result.xlsx', as_attachment=request.args.get('download', False))

@set_route(result, '/event/<event_name>/editions/<edition_name>/result')
@login_required
@admin_required
def result_page(event_name, edition_name):
    user = current_user
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()

    data = {}
    for parcours in edition.parcours:
        data[parcours.name]=get_result_data(edition, parcours)

    return render_template('result.html', user_data=user, event_data=event, edition_data=edition, result_data=data, now=datetime.now(), event_modif=True, edition_sidebar=True)