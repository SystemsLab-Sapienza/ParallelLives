import pandas as pd
import datetime
from updater_test import DBManager
import numpy as np
from utils import ensure_dir


def get_bad_spans(df):

    """return the spans that appear inside (in the same time) of bigger span

     Parameters
     ----------
     df: pd.DataFrame
        dataframe to be cleaned

     Returns
     -------
     list
        list of rows that must be deleted

     """

    span_errors = []
    ases = []
    for key, group in df.groupby(by='ASN'):
        startdate = None
        enddate = None

        new_group = group.sort_values(by=['span'], ascending=False)
        for index, row in new_group.iterrows():

            startdate = row.startdate
            enddate = row.enddate

            if len(new_group[(new_group.startdate > startdate) & (new_group.enddate < enddate)]) > 0:
                span_errors.append(new_group[(new_group.startdate > startdate) & (new_group.enddate < enddate)])
                ases.append(row.ASN)
    return span_errors



if __name__ == '__main__':

    afrinic_closed = DBManager('closed_datasets/closed_afrinic.csv', time=True, reg_time=True).df
    lacnic_closed = DBManager('closed_datasets/closed_lacnic.csv', time=True, reg_time=True).df
    apnic_closed = DBManager('closed_datasets/closed_apnic.csv', time=True, reg_time=True).df
    ripe_closed = DBManager('closed_datasets/closed_ripencc.csv', time=True, reg_time=True).df
    arin_closed = DBManager('closed_datasets/closed_arin.csv', time=True, reg_time=True).df

    all_rirs = pd.concat([afrinic_closed, lacnic_closed, apnic_closed, ripe_closed, arin_closed])

    all_rirs.reset_index(inplace=True)

    all_rirs.drop(columns=['index'], inplace=True)

    bad_spans = get_bad_spans(all_rirs)

    bad_spans_df = pd.concat(bad_spans)

    all_rirs.drop(bad_spans_df.index, inplace=True)

    all_rirs['regDate'] = np.where((all_rirs.regDate > all_rirs.startdate),
                             all_rirs.startdate,
                             all_rirs.regDate)

    ensure_dir('final_datasets')

    all_rirs.to_csv('final_datasets/all_rirs_final.csv', index=False)


