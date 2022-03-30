from flask import Flask, render_template, request, send_file
from werkzeug import secure_filename
import csv_parser
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/bank_audit', methods=['GET'])
def bank_audit():
    return render_template('upload.html')

@app.route('/paid_data', methods = ['POST'])
def upload_paid_file():
    paid_data = request.files['file1']
    buckets = request.files['file2']  
    bank_name = request.form['text']
    paid_data_name = paid_data.filename[:-4]
    buckets_name = buckets.filename[:-4]
    paid_data_name = paid_data_name.replace(" ", "")
    buckets_name = buckets_name.replace(" ", "")
    paid_data.save(secure_filename(paid_data_name + '.xls'))
    buckets.save(secure_filename(buckets_name + '.csv'))
    csv_parser.parse_data_paid(paid_data_name, buckets_name, bank_name)
    os.remove(paid_data_name + '.xls')
    os.remove(buckets_name + '.csv')
    #if request.method == 'POST':
    #    return send_file('out\\' + buckets_name + '_PAID.csv', as_attachment=True)
    #elif request.method == 'GET':
    csv_list = csv_parser.csv_to_list('out\\' + buckets_name + '_PAID.csv')
    header = ['End Date', 'Bank', 'Actual Amount', 'Bank Stated Amount', 'Difference']
    return render_template('data_table.html', csv_list = csv_list, filename = 'out\\' + buckets_name + '_PAID.csv', header = header)

@app.route('/rcv_data', methods = ['POST'])
def upload_rcv_file():
    paid_data = request.files['file1']
    buckets = request.files['file2']  
    bank_name = request.form['text']
    paid_data_name = paid_data.filename[:-4]
    buckets_name = buckets.filename[:-4]
    paid_data_name = paid_data_name.replace(" ", "")
    buckets_name = buckets_name.replace(" ", "")
    paid_data.save(secure_filename(paid_data_name + '.xls'))
    buckets.save(secure_filename(buckets_name + '.csv'))
    csv_parser.parse_data_rcv(paid_data_name, buckets_name, bank_name)
    os.remove(paid_data_name + '.xls')
    os.remove(buckets_name + '.csv')
    #if request.method == 'POST':
    #    return send_file('out\\' + buckets_name + '_RCV.csv', as_attachment=True)
    #elif request.method == 'GET':
    csv_list = csv_parser.csv_to_list('out\\' + buckets_name + '_RCV.csv')
    header = ['End Date', 'Bank', 'Actual Amount', 'Bank Stated Amount', 'Difference']
    return render_template('data_table.html', csv_list = csv_list, filename = 'out\\' + buckets_name + '_RCV.csv', header = header)

@app.route('/margins', methods = ['GET'])
def margins():
    return render_template('margins.html')

@app.route('/year_data', methods = ['POST'])
def year_data():
    inv_data = request.files['file1']
    crdr_data = request.files['file2']
    bills_data = request.files['file3']
    expenses_data = request.files['file4']
    from_year = int(request.form['text1'])
    to_year = int(request.form['text2'])
    city_code = request.form['text3']
    inv_data_name = inv_data.filename
    crdr_data_name = crdr_data.filename
    bills_data_name = bills_data.filename
    expenses_data_name = expenses_data.filename
    inv_data_name = inv_data_name.replace(" ", "")
    crdr_data_name = crdr_data_name.replace(" ", "")
    bills_data_name = bills_data_name.replace(" ", "")
    expenses_data_name = expenses_data_name.replace(" ", "")
    inv_data.save(secure_filename(inv_data_name))
    crdr_data.save(secure_filename(crdr_data_name))
    bills_data.save(secure_filename(bills_data_name))
    expenses_data.save(secure_filename(expenses_data_name))
    outfile_name = 'out/EBIT_' + city_code + '_' + request.form['text1'] + '-' + request.form['text2'] + '.csv'
    csv_parser.combine_data_to_csv(inv_data_name, crdr_data_name, bills_data_name, expenses_data_name, outfile_name, 'YEAR', from_year, to_year, city_code)
    csv_list = csv_parser.csv_to_list(outfile_name)
    os.remove(inv_data_name)
    os.remove(bills_data_name)
    os.remove(crdr_data_name)
    os.remove(expenses_data_name)
    header = ['Year', 'Invoice', 'CR/DR', 'Bills', 'Margins', 'Expenses', 'EBIT']
    return render_template('data_table.html', csv_list = csv_list, filename = outfile_name, header = header)

@app.route('/month_data', methods = ['POST'])
def month_data():
    inv_data = request.files['file1']
    crdr_data = request.files['file2']
    bills_data = request.files['file3']
    expenses_data = request.files['file4']
    from_year = int(request.form['text1'])
    to_year = int(request.form['text2'])
    city_code = request.form['text3']
    inv_data_name = inv_data.filename
    crdr_data_name = crdr_data.filename
    bills_data_name = bills_data.filename
    expenses_data_name = expenses_data.filename
    inv_data_name = inv_data_name.replace(" ", "")
    crdr_data_name = crdr_data_name.replace(" ", "")
    bills_data_name = bills_data_name.replace(" ", "")
    expenses_data_name = expenses_data_name.replace(" ", "")
    inv_data.save(secure_filename(inv_data_name))
    crdr_data.save(secure_filename(crdr_data_name))
    bills_data.save(secure_filename(bills_data_name))
    expenses_data.save(secure_filename(expenses_data_name))
    outfile_name = 'out/EBIT_' + city_code + '_' + request.form['text1'] + '-' + request.form['text2'] + '.csv'
    csv_parser.combine_data_to_csv(inv_data_name, crdr_data_name, bills_data_name, expenses_data_name, outfile_name, 'MONTH', from_year, to_year, city_code)
    csv_list = csv_parser.csv_to_list(outfile_name)
    os.remove(inv_data_name)
    os.remove(bills_data_name)
    os.remove(crdr_data_name)
    os.remove(expenses_data_name)
    header = ['Month', 'Invoice', 'CR/DR', 'Bills', 'Margins', 'Expenses', 'EBIT']
    return render_template('data_table.html', csv_list = csv_list, filename = outfile_name, header = header)

@app.route('/download', methods = ['POST'])
def download_csv():
    return send_file(request.form['filename'], as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
