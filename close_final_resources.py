from updater_test import DBManager
import numpy as np

df = DBManager('final_datasets/all_rirs_final.csv', reg_time=True, time=True, step='second')

df.first_policy()

df = DBManager('final_datasets/all_standard_policy.csv', reg_time=True, time=True, step='second')

df.apply_afrinic_policy()

df = DBManager('final_datasets/administrative_lifetimes.csv').df

cutted_df = df[df.startdate <= '2021-03-01']

cutted_df['enddate'] = np.where((cutted_df.enddate > '2021-03-01'), '2021-03-01', cutted_df.enddate)

cutted_df.to_csv('final_datasets/administrative_lifetimes.csv', index=False)