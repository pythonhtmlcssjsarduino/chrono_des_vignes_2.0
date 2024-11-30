from xlsxwriter import Workbook
from icecream import ic

name = ['parcours 1', 'parcours 2']
data = [['place', 'nom', 'prénom', 'dossard', 'temps'],
           [1, 'toi', 'tu', 34, '0:00:00'],
           *[[i, 'aurelien', 'maurer', 32, '0:00:42'] for i in range(2, 50)]]

workbook = Workbook('tests/xlsx_test.xlsx')
for parcours_data in [data]*2:
    worksheet = workbook.add_worksheet()
    for y, rows in enumerate(parcours_data[1:]):
        for x, cell in enumerate(rows):
            worksheet.write(y, x, cell)
    worksheet.add_table(0,0,y,x, {'columns': [{'header': h} for h in parcours_data[0]], 'autofilter': False})
workbook.close()
