import pandas as pd
from updater_test import DBManager
import os
from utils import ensure_dir


def group_by_regdate(df):
    """return a dataframe whose ases have been group by registration date

     Parameters
     ----------
     df: pd.DataFrame
        dataframe to be grouped by registration date

     Returns
     -------
     pd.DataFrame
        time between the dates as timedelta

     """

    stats_per_regdate = []
    for key, group in df.groupby(by=['ASN', 'regDate']):
        if len(group.index) > 1:
            startdate = group.iloc[[0]].startdate.values[0]
            asn = group.iloc[[0]].ASN.values[0]
            regdate = group.iloc[[0]].regDate.values[0]
            enddate = group.iloc[[-1]].enddate.values[0]
            opaque_id = group.iloc[[-1]].opaque_id.values[0]
            stats_per_regdate.append(
                {'ASN': asn, 'regDate': regdate, 'startdate': startdate, 'enddate': enddate,
                 'opaque_id': opaque_id})  # , 'span': get_active_time(startdate, enddate)})
        else:
            stats_per_regdate.append(
                {'ASN': group.ASN.values[0], 'regDate': group.regDate.values[0], 'startdate': group.startdate.values[0],
                 'enddate': group.enddate.values[0],
                 'opaque_id': group.opaque_id.values[0]})  # , 'span': group.span.values[0]})
    return pd.DataFrame(stats_per_regdate)


if __name__ == '__main__':

    ensure_dir('first_step')

    for rir in os.listdir('cleaned_resources'):

        db = DBManager(os.path.join('cleaned_resources', rir), time=True, reg_time=True)

        df = db.df

        df_per_reg_date = group_by_regdate(df)

        df.drop(columns=['start', 'country', 'value', 'opaque_id'], inplace=True)

        df_per_reg_date.drop(columns='opaque_id', inplace=True)

        print('first for')
        rows_count = len(df_per_reg_date)
        for index, row in df_per_reg_date.iterrows():
            print(rows_count)
            rows_count -= 1
            df.drop(df[(df.ASN == row.ASN) & (df.startdate >= row.startdate) & (df.enddate <= row.enddate)].index,
                    inplace=True)

        df_per_reg_date['registry'] = rir.split('.')[0].split('_')[-1]
        df_per_reg_date['status'] = 'allocated'

        merged_df = pd.concat([df, df_per_reg_date])

        del df

        merged_df.reset_index(inplace=True)

        merged_df.drop(columns=['index'], inplace=True)

        merged_df.sort_values(by=['ASN', 'startdate', 'enddate'], inplace=True)

        print('second for')
        rows_count = len(df_per_reg_date)
        for index, row in df_per_reg_date.iterrows():
            print(rows_count)
            rows_count -= 1
            merged_df.drop(merged_df[(merged_df.ASN == row.ASN) & (merged_df.startdate > row.startdate) &
                                     (merged_df.enddate < row.enddate)].index, inplace=True)


        merged_df.to_csv('first_step/first_{}.csv'.format(rir.split('.')[0].split('_')[-1]), index=False)



