import bz2
import gzip
import os
import pandas as pd
import datetime


def get_rir_from_file(file_name: str) -> str:
    """

    :param file_name: str
        path to the file
    :return: str
        name of the rir that produced the file
    """
    return os.path.basename(file_name).split('-')[1]


def read_bz(path: str) -> str:
    """

    :param path: str
        path to the file
    :return: str
        text of the file
    """

    with bz2.BZ2File(os.path.join(path), 'r') as fin:
        return fin.read()


def read_gz(path: str) -> str:
    """

    :param path: str
        path to the file
    :return: str
        text of the file
    """

    with gzip.open(os.path.join(path), 'rt') as fin:
        return fin.read()


def read_plain(path: str) -> str:
    """

    :param path: str
        path to the file
    :return: str
        text of the file
    """
    with open(os.path.join(path), 'r') as fin:
        return fin.read()


def read_file(file_path: str) -> str:
    """

    :param path: str
        path of the file
    :return: str
        text of the file
    """

    if file_path.split('.')[-1] == 'gz':

        return read_gz(file_path)

    elif file_path.split('.')[-1] == 'bz2':

        return read_bz(file_path)

    else:

        return read_plain(file_path)


def read_database(path_file):
    df = pd.read_csv(path_file, parse_dates=['startdate', 'enddate', 'regDate'], keep_default_na=False)

    if df.regDate.dtype != float:
        df.regDate = pd.to_datetime(df.regDate, format='%Y%m%d', errors='coerce')
    return df


def get_day_of_file(file_name: str) -> datetime.datetime:
    file_name = os.path.basename(file_name)
    if '.' in file_name:
        file_name = file_name.split('.')[0]

    return datetime.datetime.strptime(os.path.basename(file_name).split('-')[-1], '%Y%m%d')


def check_equality(df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> bool:
    """

    :param df: pd.DataFrame
        dataframe updated by the script
    :param ground_truth_df: pd.DataFrame
        dataframe with the ground truth
    :return: bool
        True if they are equale, False otherwise
    """
    df.sort_values(by=['ASN', 'enddate'], inplace=True)
    ground_truth_df.sort_values(by=['ASN', 'enddate'], inplace=True)
    df.reset_index(inplace=True)
    ground_truth_df.reset_index(inplace=True)
    df.drop(columns=['index'], inplace=True)
    ground_truth_df.drop(columns=['index'], inplace=True)
    return df.equals(ground_truth_df)

def check_difference(df_new, df_old):

    diff_df = pd.merge(df_new, df_old, how='outer', indicator='Exist')
    diff_df = diff_df.loc[diff_df['Exist'] != 'both']
    return diff_df

def ensure_dir(file_path):
    directory = file_path
    if not os.path.exists(directory):
        os.makedirs(directory)
