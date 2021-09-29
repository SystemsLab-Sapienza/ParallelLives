from updater_test import DBManager
import os
from utils import ensure_dir

if __name__ == '__main__':

    ensure_dir('closed_datasets')

    for rir in os.listdir('first_step'):

        db = DBManager(os.path.join('first_step', rir), time=True, reg_time=True, step='first')
        db.first_policy()

