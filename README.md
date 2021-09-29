# The parallel lives of Autonomous Systems: ASN Allocations vs. BGP
Additional material for paper "The parallel lives of Autonomous Systems: ASN Allocations vs. BGP", to appear in IMC ’21.

File description:
---------
cleaned_resources : In this folder there is a tar file "cleaned_datasets_rirs.tar.xz" that contains  all the RIRs datasets representing the ASNs spans reconstructed using the delegation files in csv format.

final_datasets: This folder contains administrative_lifetimes.csv, a csv file with all the administrative lives of the ASNs.

close_span_per_RIR.py: code to apply the first step to build the administrative lives.

implement_policy.py: code that implement the general policies of the RIRs to close the administrative lives.

remove_inner_span.py: code to remove inner allocations.

close_final_resources.py: code to generate the final administrative lives dataset "administrative_lifetimes.csv".


**How to produce the administrative dataset:**

1- Download the folder cleaned_resources and untar "cleaned_datasets_rirs.tar.xz".

2- Run close_span_per_rir.py.

3- Run implement_policy.py

4- Run remove_inner_span.py

4- Run close_final_resource.py.
