#!/usr/bin/python

import argparse
import os
from datetime import datetime, timedelta


import requests
import pygal
from jinja2 import Environment, FileSystemLoader


URL = 'http://projects.knmi.nl/klimatologie/daggegevens/getdata_dag.cgi';
VARS = 'RH'
DATE_FORMAT = '%Y%m%d'

# Old data https://projects.knmi.nl/klimatologie/daggegevens/index.cgi
# YYYYMMDD = datum (YYYY=jaar,MM=maand,DD=dag);
# DR       = Duur van de neerslag (in 0.1 uur) per uurvak;
def create_svg(station):
    start = datetime.now() - timedelta(days=60) # ~ 2 months
    req = requests.post(URL, data={'stns': station, 'start': start, 'vars': VARS})
    if req.status_code != 200:
        print('KNMI API borked')
        return

    bar_chart = pygal.Bar(height=400)
    bar_chart.title = 'Rain per day (in mm)'

    rain_data = []
    date_data = []
    for row in req.text.split('\n'):
        if row.startswith('#') or not row:
            continue

        _, datestr, rain = row.split(',')
        rain = int(rain) * 0.1
        if rain < 0:
            rain = 0
        date = datetime.strptime(datestr, DATE_FORMAT)
        date_data.append(date.strftime('%d-%m'))
        rain_data.append(rain)

    bar_chart.x_labels = date_data
    bar_chart.x_label_rotation = 45
    bar_chart.add('Rain', rain_data)
    return bar_chart.render(is_unicode=True)


def main():
    directory = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(description='Generate a raingraph')
    parser.add_argument('--station', type=int, default=344)
    parser.add_argument('--directory', type=str, default=directory)
    args = parser.parse_args()

    jinja2_env = Environment(loader=FileSystemLoader(directory), trim_blocks=True)
    svg = create_svg(args.station)


    with open(f'{args.directory}/index.html', 'w') as rain_file:
        rain_file.write(jinja2_env.get_template('template.html').render(svg=svg))


if __name__ == "__main__":
    main()
