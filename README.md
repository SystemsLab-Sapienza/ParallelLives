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

## Code

**Steps to produce the administrative dataset**

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

**Steps to produce the operational dataset**

1. Run ```bgp_close_span.py```

```
python3 bgp_close_span.py
```

This code takes as input the ```operational_lifetimes_raw.csv``` and produces the  ```operational_lifetimes.csv``` operational dataset merging all the operational lives of the same ASN that are closer than 30 days.
