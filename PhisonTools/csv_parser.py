import xlrd
import csv
import datetime as dt
import os

def serial_to_date(serial):
    temp = dt.datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = dt.timedelta(float(serial))
    return temp + delta

def excel_to_csv(xls_filename, csv_filename, type_data):
    if type_data == 'PAID':
        index = 5
    elif type_data == 'RCV':
        index = 6
    else:
        index = 5
    with xlrd.open_workbook(xls_filename) as wb:
        sh = wb.sheet_by_index(0)  # or wb.sheet_by_name('name_of_the_sheet_here')
        with open(csv_filename, 'w', newline = '') as f:   # open('a_file.csv', 'w', newline="") for python 3
            c = csv.writer(f)
            for r in range(sh.nrows):
                row = sh.row_values(r)
                row[0] = serial_to_date(row[0])
                row[index] = serial_to_date(row[index])
                if row:
                    c.writerow(row) 
                

def combine_month_numbers(csv_in, csv_out, buckets, bank_name, bucket_dict, type_data):
    buckets.append(dt.date(9999, 12, 31))
    with open(csv_out, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Date', 'Bank', 'Actual Amount', 'Bank Stated Amount', 'Difference'])
        with open(csv_in) as infile:
            reader = csv.reader(infile, delimiter=',')

            bank_dict = {}
            bucket_index = 0
            for row in reader:
                if row:
                    if type_data == 'PAID':
                        dateind = 5
                    else:
                        dateind = 6
                    date = (dt.datetime.strptime(row[dateind], '%Y-%m-%d %H:%M:%S')).date()
                    if date > buckets[bucket_index]:
                        for key, value in bank_dict.items():
                            if key == bank_name:
                                if type_data == 'PAID':
                                    num = 0
                                else:
                                    num = 1
                                bank_amount = (bucket_dict[dt.datetime.strftime(buckets[bucket_index], '%m/%d/%Y')])[num]
                                print(bank_amount, round(value, 2))
                                if bucket_index != 0:
                                    if bank_amount != round(value, 2):
                                        writer.writerow([buckets[bucket_index], key, round(value, 2), bank_amount, round(value - bank_amount, 2)])
                                    else:
                                        writer.writerow([buckets[bucket_index], key, round(value, 2), bank_amount, round(value - bank_amount, 2)])
                            bank_dict[key] = 0
                        bucket_index += 1
                    if type_data == 'PAID':
                        rowind1 = 4
                        rowind2 = 3
                    else:
                        rowind1 = 3
                        rowind2 = 4
                    if row[rowind1] not in bank_dict:
                        bank_dict[row[rowind1]] = 0
                    if row[rowind2]:
                        bank_dict[row[rowind1]] += float(row[rowind2])

def csv_to_buckets(bucket_file):
    buckets = []
    bucket_dict = {}
    with open(bucket_file) as infile:
        reader = csv.reader(infile, delimiter=',')
        next(reader, None)
        for row in reader:
            if row[0] and row[1] and row[2]:
                date = dt.datetime.strptime(row[0], '%m/%d/%Y')
                buckets.append(date.date())
                bucket_dict[dt.datetime.strftime(date, '%m/%d/%Y')] = (float(row[1]), float(row[2]))
    return buckets, bucket_dict

def csv_to_list(csv_file):
    csv_list = []
    with open(csv_file) as infile:
        reader = csv.reader(infile, delimiter=',')
        next(reader, None)
        for row in reader:
            csv_list.append(row)
    return csv_list

def parse_data_paid(paid_data, filename, bank_name):
    paid_csv = paid_data + '.csv'
    excel_to_csv(paid_data + '.xls', paid_csv, 'PAID')
    dates, numbers = csv_to_buckets(filename + '.csv')
    combine_month_numbers(paid_csv, 'out/' + filename + '_PAID.csv', dates, bank_name, numbers, 'PAID')
    os.remove(paid_data + '.csv')

def parse_data_rcv(rcv_data, filename, bank_name):
    rcv_csv = rcv_data + '.csv'
    excel_to_csv(rcv_data + '.xls', rcv_csv, 'RCV')
    dates, numbers = csv_to_buckets(filename + '.csv')
    combine_month_numbers(rcv_csv, 'out/' + filename + '_RCV.csv', dates, bank_name, numbers, 'RCV')
    os.remove(rcv_data + '.csv')

def related_to_list(xls_filename, related_type):
    if related_type == 'INV':
        index = 7
        city = 20
    elif related_type == 'BILL':
        index = 5
        city = 18
    elif related_type == 'CRDR':
        index = 8
        city = 16
    else:
        index = 7
        city = 20
    dic = {}
    dic['ALL'] = {}
    with xlrd.open_workbook(xls_filename) as wb:
        sh = wb.sheet_by_index(0)  # or wb.sheet_by_name('name_of_the_sheet_here')
        for r in range(sh.nrows):
            row = sh.row_values(r)
            year = serial_to_date(row[0]).year
            month = serial_to_date(row[0]).month
            if row[city] not in dic:
                dic[row[city]] = {}
            if year not in dic[row[city]]:
                dic[row[city]][year] = {}
                for i in range(1, 13):
                    dic[row[city]][year][i] = 0
            dic[row[city]][year][month] += row[index]
            if year not in dic['ALL']:
                dic['ALL'][year] = {}
                for i in range(1, 13):
                    dic['ALL'][year][i] = 0
            dic['ALL'][year][month] += row[index]
    return dic

def expenses_to_list(xls_filename):
    dic = {}
    dic['ALL'] = {}
    with xlrd.open_workbook(xls_filename) as wb:
        sh = wb.sheet_by_index(0)  # or wb.sheet_by_name('name_of_the_sheet_here')
        for r in range(sh.nrows):
            row = sh.row_values(r)
            date = row[0]
            date_split = date.split('/')
            if len(date_split) == 3:
                if len(date_split[0]) == 1:
                    date_split[0] = '0' + date_split[0]
                if len(date_split[1]) == 1:
                    date_split[1] = '0' + date_split[1]
                date = dt.datetime.strptime(date_split[0] + '/' + date_split[1] + '/' + date_split[2], '%m/%d/%Y')
                year = date.year
                month = date.month
                try:
                    city = row[1][:3]
                    if city not in dic:
                        dic[city] = {}
                    if year not in dic[city]:
                        dic[city][year] = {}
                        for i in range(1, 13):
                            dic[city][year][i] = 0
                    dic[city][year][month] += row[15] - row[16]
                except:
                    print(row[1])
                if year not in dic['ALL']:
                    dic['ALL'][year] = {}
                    for i in range(1, 13):
                        dic['ALL'][year][i] = 0
                dic['ALL'][year][month] += row[15] - row[16]
    return dic
        
def combine_data_to_csv(inv_file, crdr_file, bill_file, exp_file, csv_out, type_date, start_year, end_year, city):
    year_list = list(range(start_year, end_year + 1))
    month_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    inv_dict = related_to_list(inv_file, 'INV')[city]
    crdr_dict = related_to_list(crdr_file, 'CRDR')[city]
    bill_dict = related_to_list(bill_file, 'BILL')[city]
    exp_dict = expenses_to_list(exp_file)[city]
    #print(bill_dict)
    with open(csv_out, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Year', 'Invoice', 'CR/DR', 'Bill', 'Margin', 'Expenses', 'EBIT'])
        for year in year_list:
            if type_date == 'YEAR':
                inv = 0
                crdr = 0
                bill = 0
                exp = 0
                for month in month_list:
                    try:
                        inv += inv_dict[year][month]
                    except:
                        inv = 0
                    try:
                        crdr += crdr_dict[year][month]
                    except:
                        crdr = 0
                    try:
                        bill += bill_dict[year][month]
                    except:
                        bill = 0
                    try:
                        exp += exp_dict[year][month]
                    except:
                        exp = 0
                inv = round(inv, 2)
                crdr = round(crdr, 2)
                bill = round(bill, 2)
                margin = round(inv + crdr - bill, 2)
                exp = round(exp, 2)
                ebit = round(margin - exp, 2)
                writer.writerow([year, inv, crdr, bill, margin, exp, ebit])
            elif type_date == 'MONTH':
                for month in month_list:
                    try:
                        inv = round(inv_dict[year][month], 2)
                    except:
                        inv = 0
                    try:
                        crdr = round(crdr_dict[year][month], 2)
                    except: 
                        crdr = 0
                    try:
                        bill = round(bill_dict[year][month], 2)
                    except:
                        bill = 0
                    try:
                        exp = round(exp_dict[year][month], 2)
                    except:
                        exp = 0
                    margin = round(inv + crdr - bill, 2)
                    ebit = round(margin - exp, 2)
                    writer.writerow([str(month) + '/' + str(year), inv, crdr, bill, margin, exp, ebit])
                    
                

#print(expenses_to_list('2011-2017 EXPENSES.xls'))
#combine_data_to_csv('related/2011-2017 INV List.xls', 'related/2011-2017 CRDR List.xls', 'related/2011-2017 BILL List.xls', 'related/2011-2017 EXPENSES.xls', 'out2.csv', 'MONTH', 2011, 2017, 'ALL')
#excel_paid_to_csv('old_files/files/2011-2017_CHQ_PAID.xls', 'temp.csv')
#parse_data_rcv('2011-2017_CHQ_RCV', 'BANKOFHOPE2017-2017', 'BANK OF HOPE')
#parse_data('2011-2017_CHQ_PAID', '2011-2017_CHQ_RCV',  'BBCN2015-2015', 'BANK OF HOPE')
#parse_data('2011-2017_CHQ_PAID', '2011-2017_CHQ_RCV', 'NYC2012-2015', 'BBCN Bank')
#parse_data('2011-2017_CHQ_PAID', '2011-2017_CHQ_RCV', 'HANMI2012-2014', 'HANMI BANK')
#parse_data('2011-2017_CHQ_PAID', '2011-2017_CHQ_RCV', 'BBCN2016-2016', 'BANK OF HOPE')
#parse_data('2011-2017_CHQ_PAID', '2011-2017_CHQ_RCV', 'BANKOFHOPE2017-2017', 'BANK OF HOPE')
