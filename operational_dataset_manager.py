import glob
from collections import defaultdict
import pandas as pd
import datetime
from datetime import timedelta
from datetime import datetime
import gzip
import os
import collections
import configparser


config = configparser.ConfigParser()
config.read('config/config.ini')


class DatasetManager:

    def __init__(self, file_path, visibility_th=1):
        self.visibility_th = visibility_th
        self.spans = defaultdict(list)
        self.file_path = file_path
        try:
            self.load_from_file(self.file_path)
        except FileNotFoundError:
            with open(self.file_path, 'w') as f:
                f.write('ASN,startdate,enddate\n')
            print('new dataset file created')

    def load_from_file(self, file_path):
        print('loading from file: {}'.format(file_path))
        df = pd.read_csv(file_path, comment='#')
        datetime_format = '%Y-%m-%d'
        for i, row in df.iterrows():
            self.spans[row['ASN']].append({'startdate': datetime.strptime(row['startdate'], datetime_format).date(),
                                           'enddate':  datetime.strptime(row['enddate'], datetime_format).date()})

    def populate(self, raw_file_path):
        min_date, max_date, date_list = self.get_dates(raw_file_path)
        print('populating from {} to {} '.format(min_date, max_date))
        for day in date_list:
            self.populate_single_day(day, raw_file_path)

    def populate_single_day(self, day, path):
        asns_dict = defaultdict(set)
        visibility_th = self.visibility_th
        print('populating {} '.format(day))
        for file in self.get_files_from_date(path, day):
            with gzip.open(file, 'rt') as f:
                for line in f:
                    columns = line.replace('\n', '').split('|')
                    try:
                        int(columns[0])
                    except ValueError:
                        continue
                    if columns[-1].count(',') > visibility_th:
                        asns_dict[int(columns[0])] = set(range(visibility_th + 1))
                    else:
                        peers = columns[-1].split(',')
                        asns_dict[int(columns[0])] |= set(peers)

        for asn, v in asns_dict.items():
            if len(v) > visibility_th:
                self.update_spans(asn, day.date())

    def update_spans(self, asn, date):
        if asn in self.spans:
            last = self.spans[asn][-1]
            if last['enddate'] == date - timedelta(days=1):
                self.spans[asn][-1]['enddate'] = date
            else:
                self.spans[asn].append({
                    'startdate': date,
                    'enddate': date
                })
        else:
            self.spans[asn].append({
                'startdate': date,
                'enddate': date
            })

    def write_to_file(self, file_path):
        with open(file_path, 'w+') as out:
            #out.write('# ' + str(datetime.now().isoformat(' ', 'seconds')) + '\n')
            out.write('ASN,startdate,enddate\n')
            od = collections.OrderedDict(sorted(self.spans.items()))
            for key, values in od.items():
                for span in values:
                    out.write(','.join((str(key), str(span['startdate']), str(span['enddate']))) + '\n')
        print('dumped to file: ' + file_path)

    def fill(self, threshold):
        for asn in self.spans:
            new_records = []
            record = self.spans[asn][0]
            if len(self.spans[asn]) == 1:
                new_records.append(record)
            for i, new_record in enumerate(self.spans[asn][1:]):
                if new_record['startdate'] - record['enddate'] > timedelta(days=threshold):
                    new_records.append(record)
                    record = new_record
                else:
                    record['enddate'] = new_record['enddate']
                if i == len(self.spans[asn]) - 2:
                    new_records.append(record)
            self.spans[asn] = new_records
        print('filled with threshold {}'.format(threshold))

    @staticmethod
    def get_dates(path):
        path = glob.glob(path + '*.gz')
        dates = [os.path.basename(f).split('_')[0] for f in path]
        min_date, max_date = datetime.strptime(min(dates), "%Y-%m-%d"), datetime.strptime(max(dates), "%Y-%m-%d")
        days = (max_date - min_date).days
        date_list = sorted([min_date + timedelta(days=x) for x in range(days + 1)])
        return min_date, max_date, date_list

    @staticmethod
    def get_files_from_date(path, date):
        date_str = date.strftime("%Y-%m-%d")
        #template = path + '{}_allcollectors_{}_{}ASN.asn-peer.gz'
        template = path + config['constant']['raw_file_template']
        combinations = [('ribs', 'origin'), ('ribs', 'transit'), ('updates', 'origin'), ('updates', 'transit')]
        for pair in combinations:
            yield template.format(date_str, pair[0], pair[1])


if __name__ == '__main__':
    start = datetime.now()
    raw_dataset_path = 'bgp_dataset_raw/'
    dataset_path = 'bgp_dataset/'
    operational_threshold = int(config['constant']['fill'])
    vis_th = int(config['constant']['vis_th'])

    dm = DatasetManager(raw_dataset_path + 'operational_lifetimes_raw.csv'.format(vis_th), visibility_th=vis_th)

    if config.getboolean('mode', 'extend'):
        dm.populate('bgp_dataset_raw/')
        dm.write_to_file(dataset_path + 'operational_lifetimes_raw_vis_{}.csv'.format(vis_th))

    dm.fill(30)
    dm.write_to_file(dataset_path + 'operational_lifetimes_vis_{}.csv'.format(vis_th))

    print('time: ' + str(datetime.now() - start))
