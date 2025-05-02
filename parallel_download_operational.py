from datetime import timedelta, datetime
import glob
from bgp_downloader import download
from multiprocessing import Pool
import os


def square(date):
    #os.system("python bgp_downloader.py {}".format(date))
    download('ribs', start=date + ' 15:30:00 UTC', end=date + ' 17:30:00 UTC')
    download('updates', start=date + ' 00:00:00 UTC', end=date + ' 23:59:59 UTC')

def datespan(start_date, end_date, delta):
    current_date = start_date
    while current_date < end_date:
        yield current_date
        current_date += delta


def generate_dates(start, end, delta_days):
    return datespan(start, end, delta=timedelta(days=delta_days))


if __name__ == '__main__':
    already_downloaded = glob.glob('bgp_dataset_raw/*')
    already_downloaded = [os.path.basename(f).split('_')[0] for f in already_downloaded]

    print(already_downloaded)

    file_aware = True
    dates = generate_dates(datetime(2021, 3, 1), datetime(2021, 3, 5), 1)

    dates_str = []
    for d in dates:
        d = str(d.date())
        if file_aware:
            print('date')
            print(d)
            if d in already_downloaded:
                continue
        dates_str.append(d)

    print(dates_str)

    processes = 5
    with Pool(processes=processes) as pool:
        pool.map(square, dates_str)

