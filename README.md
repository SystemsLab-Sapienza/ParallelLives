# The parallel lives of Autonomous Systems: ASN Allocations vs. BGP
Additional material for paper [The parallel lives of Autonomous Systems: ASN Allocations vs. BGP](https://www.cc.gatech.edu/~adainotti6/pubs/imc2021-231.parallel_lives.pdf),  to appear in IMC ’21.

Authors:
[@EugenioNemmi](https://github.com/EugenioNemmi), [@francescosassi](https://github.com/francescosassi), [@Ansijax](https://github.com/Ansijax), [@ctestart](https://github.com/ctestart), [@AlessandroMei](http://wwwusers.di.uniroma1.it/~mei/), [@albertodainotti](https://github.com/albertodainotti)


If you use this dataset please cite:

```
@inproceedings{nemmi2021parallel,
  title={The parallel lives of Autonomous Systems: ASN Allocations vs. BGP},
  author={Nemmi, Eugenio Nerio and Sassi, Francesco and La Morgia, Massimo and Testart, Cecilia and Dainotti, Alberto},
  booktitle={ACM SIGCOMM Conference on Internet Measurement, IMC},
  volume={21},
  year={2021}
}
```

This repository contains the operational and administrative datasets used in the paper with the code to generate them.

## Data

The ```administrative_lifetimes.csv``` file contains the dataset of administrative lives. 
Each row of this file contains::
* **ASN**: the Autonomous System Number. 
* **startdate**: the start date of the ASN's administrative life.
* **enddate**: the end date of the ASN's administrative life.
* **regDate**: the registration date of the ASN's administrative life.
* **status**: the status of the resource. The possible statuses are: ```{available, allocated, reserved}```.
* **registry**: The registry that the ASN has been assigned to. One of: ```{afrinic, apnic, arin, lacnic, ripencc}```.


We also provide ```cleaned_datasets_rirs.tar.xz```, a more "raw" version of the dataset obtained by processing the delegation files after applying our restoration methodology.  This dataset is different from the previous one because it does not consider the RIRs policies. To produce the ```administrative_lifetimes.csv``` from this dataset you can run the scripts that apply the RIRs policies as described below.

## Steps to produce the administrative dataset

1. Extract the ```cleaned_datasets_rirs.tar.xz``` file that is inside the ```cleaned_resources``` folder.

```
tar -xvf cleaned_datasets_rirs.tar.xz
```

2. Run ```close_span_per_rir.py```. 

```
python3 close_span_per_rir.py
```

3. Run ```implement_policy.py```. 

```
python3 implement_policy.py
```

4. Run ```remove_inner_span.py```.

```
python3 remove_inner_span.py
```

5. Run ```close_final_resource.py```. 

```
python3 close_final_resource.py
```

This code generates the final administrative lives dataset: ```administrative_lifetimes.csv```. 

## Steps to Reproduce the Operational Dataset

To reproduce the original dataset used in our paper, start from the file `operational_lifetimes_raw.csv`, which contains BGP data up to **2021-03-01**.

The script `operational_dataset_manager.py` takes this raw input and produces `operational_lifetimes.csv`, merging operational lifetimes of the same ASN that are separated by fewer than 30 days.

```
python3 operational_dataset_manager.py
```

## [Optional] Steps to Extend the Operational Dataset

**Note:** To enable dataset extension, set the `extend` flag to `True` in the `config/config.ini` file.

### 1. Download Raw RIB and Update Files

Use the `parallel_download_operational.py` script to download BGP RIB and update files. You can specify the start and end dates for data collection, as well as the number of parallel cores to use for faster downloading.

```
python3 parallel_download_operational.py
```

### 2. Process Raw Files into Operational Dataset

Once the raw files have been downloaded, process them using the operational_dataset_manager.py script. This script supports:

- A visibility threshold to define when an ASN is considered operational.

- A merging threshold (in days) to join multiple operational lifetimes of the same ASN.

By default, these values are set to match the configuration used in our paper (`visibility = 1`, `merging threshold = 30 days`). You can modify these parameters in `config/config.ini`.

```
python3 operational_dataset_manager.py
```

