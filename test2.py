import pandas
import csv
import datetime


def date_getter():
    today = datetime.date.today()
    hour = datetime.datetime.now().hour
    if hour >= 20:  # time is past 8 pm, make the date tomorrow
        today = datetime.date.today() + datetime.timedelta(days=1)
    return today
i=0
with open('Data/{}/FanDuel-NBA-2018-10-21-29270-entries-upload-template.csv'.format(date_getter()), mode='r') as fd_file:
        fd_reader = csv.reader(fd_file)
        entries = []
        for row in fd_reader:
            if row[0] == '':
                continue
            entries.append(row)
        print(entries)
        #for i in range(len(fd_reader)):
        #    line = [j.strip('"').strip('\n') for j in fd_file.readline().split(',')]
