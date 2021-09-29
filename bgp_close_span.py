from collections import defaultdict
import pandas as pd
import datetime
from datetime import timedelta
from datetime import datetime
import collections
from utils import ensure_dir


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
        datetime_format = '%Y-%m-%d %H:%M:%S'
        for i, row in df.iterrows():
            self.spans[row['ASN']].append({'startdate': datetime.strptime(row['startdate'], datetime_format).date(),
                                           'enddate': datetime.strptime(row['enddate'], datetime_format).date()})

    def write_to_file(self, file_path):
        with open(file_path, 'w+') as out:
            out.write('ASN,startdate,enddate\n')
            od = collections.OrderedDict(sorted(self.spans.items()))
            for key, values in od.items():
                for span in values:
                    out.write(','.join((str(key), str(span['startdate']), str(span['enddate']))) + '\n')

        return pd.read_csv(file_path, comment='#')

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


if __name__ == '__main__':
    ensure_dir('bgp_dataset')
    timeout = 30
    dm = DatasetManager('bgp_dataset_raw/operational_lifetimes_raw.csv')
    dm.fill(timeout)
    out_path = 'bgp_dataset/operational_lifetimes.csv'
    df = dm.write_to_file(out_path)
