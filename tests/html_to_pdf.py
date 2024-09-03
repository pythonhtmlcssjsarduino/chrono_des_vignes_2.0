import pdfkit
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

#pdfkit.from_url('http://google.com', 'out.pdf', configuration=config)

pdfkit.from_file('tests/chart.html', output_path='tests/chart.pdf', configuration=config, options={'javascript-delay':'5000', 'no-stop-slow-scripts':''})