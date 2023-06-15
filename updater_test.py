import pandas as pd
import datetime
import os



class Life:
    """
    A class used to represent a single life of ASN

    ...

    Attributes
    ----------
    index : int
        index of the row
    enddate : str
        last day of the span belonging to the same life

    """

    def __init__(self, index, enddate):
        self.index = index
        self.enddate = enddate



class DBManager:
    """
    A class used to manage the DataBase and its operation

    ...

    Attributes
    ----------
    df : pd.DataFrame
        DataFrame that represent the database if it has been rad, empty otherwise
    file_path : str
        path to the database if given

    """

    def __init__(self, file_path=None, time=False, reg_time=True, step='first'):
        self.df = pd.DataFrame()
        self.file_path = file_path
        self.time = time
        self.reg_time = reg_time
        self.to_parse = []
        self.step = step
        if step == 'first':
            self.out_file = 'closed_datasets/closed_{}.csv'.format(os.path.basename(self.file_path).split('_', 1)[1].split('.')[0])
        else:
            self.out_file = 'final_datasets/all_standard_policy.csv'
        if file_path:
            self.read_database(file_path)

    def read_database(self, file_path: str) -> pd.DataFrame:
        """

        :param afrinic:  Bool
            true if it is called for afrinic policy implementation
        :param file_path: str
            string of path to the file
        :return: pd.DataFrame
            database as dataframe object
        """
        self.file_path = file_path

        if self.reg_time:
            self.to_parse.append('regDate')

        if self.time:

            self.to_parse += ['startdate', 'enddate']

        df = pd.read_csv(file_path, dtype={'status': 'category', 'registry': 'category', 'country': 'category', 'opaque_id':'category', 'value':'int16'},
                             parse_dates=self.to_parse, keep_default_na=False)


        self.df = df
        return df

    def first_policy(self):
        """

        :param df: pd.DataFrame
            dataframe to enforce with standard policy
        :return: pd.DataFrame
            dataframe with enforced standard policy
        """

        df = self.df

        reg_name = df.registry.unique()[0]

        if 'start' in df or 'country' in df or 'value' in df:

            df.drop(columns=['value', 'opaque_id', 'start', 'country'], inplace=True)

        first = True

        new_dfs = []

        to_write_df = pd.DataFrame()

        print('starting first policy implementation')
        for key, group in df.groupby('ASN'):  # type: (object, pd.DataFrame)

            group.regDate.fillna('', inplace=True)

            new_df_groups = []

            group.sort_values('startdate', inplace=True)

            record = None
            reserved = []
            reg_dates = []
            for index, row in group.iterrows():

                if row.status == 'allocated':
                    if not record:
                        if reserved:
                            new_df_groups += reserved
                            reserved = []
                        record = row.to_dict()
                        record['last_reg'] = record['regDate']
                        # reg_dates.append(record['regDate'])
                    else:

                        if row['startdate'] <= (record['enddate'] + datetime.timedelta(days=1)) or row['regDate'] == \
                                record['last_reg'] or row['regDate'] == record['regDate']:
                            record['enddate'] = row['enddate']
                            record['registry'] = row['registry']
                            record['last_reg'] = row['regDate']

                            reserved = []


                        else:

                            new_df_groups.append(record)
                            record = row.to_dict()
                            record['last_reg'] = record['regDate']

                            if len(reserved) > 0:
                                new_df_groups += reserved
                                reserved = []

                else:

                    if not reserved:
                        reserved.append(row.to_dict())
                    else:
                        if row['startdate'] <= reserved[-1]['enddate'] + datetime.timedelta(days=1) and row['status'] == \
                                reserved[-1]['status']:
                            reserved[-1]['enddate'] = row['enddate']
                            reserved[-1]['registry'] = row['registry']
                        else:
                            reserved.append(row.to_dict())

            if record:
                new_df_groups.append(record)

            if reserved:
                new_df_groups += reserved

            new_df_groups = pd.DataFrame(new_df_groups).sort_values(by='startdate')
            if 'last_reg' in new_df_groups.columns:
                new_df_groups.drop(columns=['last_reg'], inplace=True)

            new_dfs.append(new_df_groups)


            if len(new_dfs) == 5000:

                to_write_df = pd.concat(new_dfs)

                to_write_df.startdate = pd.to_datetime(to_write_df.startdate)
                to_write_df.enddate = pd.to_datetime(to_write_df.enddate)
                to_write_df['span'] = (to_write_df.enddate - to_write_df.startdate).dt.days + 1
                to_write_df.regDate = pd.to_datetime(to_write_df.regDate, errors='coerce')

                if first:

                    to_write_df.to_csv(self.out_file, index=False)
                    first = False

                else:

                    to_write_df.to_csv(self.out_file, mode='a', header=False, index=False)

                new_dfs = []

        if len(new_dfs) > 0:

            to_write_df = pd.concat(new_dfs)

            to_write_df.startdate = pd.to_datetime(to_write_df.startdate)
            to_write_df.enddate = pd.to_datetime(to_write_df.enddate)
            to_write_df['span'] = (to_write_df.enddate - to_write_df.startdate).dt.days + 1
            to_write_df.regDate = pd.to_datetime(to_write_df.regDate, errors='coerce')

            if first:

                to_write_df.to_csv(self.out_file, index=False)
                first = False

            else:

                to_write_df.to_csv(self.out_file, mode='a', header=False, index=False)


    def apply_afrinic_policy(self):
        """

        :param df: pd.DataFrame
            dataframe to enforce with afrinic policy
        :return: pd.DataFrame
            dataframe with enforced afrinic policy
        """

        df = self.df

        print('starting afrinic policy implementation...')

        to_delete = []
        df.regDate.fillna('', inplace=True)
        for key, group in df.groupby('ASN'):

            life = None

            for index, row in group.iterrows():

                if len(group[(group.status == 'allocated') & (group.registry == 'afrinic')]) != 0:

                    last_index = group[(group.status == 'allocated') & (group.registry == 'afrinic')].index[-1]

                else:
                    break

                if index > last_index:
                    break

                if row.registry == 'afrinic':

                    if not life and row.status == 'allocated':

                        life = Life(index, row.enddate)

                    else:
                        if not life:
                            continue
                        if row.startdate == (life.enddate + datetime.timedelta(days=1)) and row.status != 'available':

                            to_delete.append(index)
                            life.enddate = row.enddate
                            df.loc[life.index, 'enddate'] = life.enddate

                        else:
                            if row.status == 'allocated':
                                life = Life(index, row.enddate)
                            else:
                                life = None

                else:
                    if life:
                        life = None

        compacted_df = df.drop(to_delete)

        compacted_df.regDate = pd.to_datetime(compacted_df.regDate, errors='coerce')
        compacted_df.span = (compacted_df.enddate - compacted_df.startdate).dt.days + 1

        compacted_df.to_csv('final_datasets/administrative_lifetimes.csv', index=False)