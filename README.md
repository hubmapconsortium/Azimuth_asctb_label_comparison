# Azimuth-asctb-label-comparison

## Work-flow Venn Diagraph

![alt text](Azimuth_asctb_label_comparison/Data/flow.jpg "Optional Title")

## Methodology

## Comparison of Azimuth and ASCT+B using Ubergraph to extract parent labels:
### Cases to match Label Authors between Azimuth and ASCT+B:
* We do perfect matches between Azimuth label Authors and the label and label authors of ASCT-B tables.
* The mismatched Labels will be used to generate Parent Labels and do further matching
### Cases to match mismatched Labels with Ubergraph Labels:
* Cleaning the labels – This includes removing spaces, special characters and converting it into lower case.
* Matching -
1.      Direct matches between ASCTB/Azimuth label authors and Ubergraph Labels.
2.      Direct matches between ASCTB/Azimuth label authors and Ubergraph Synonyms.
3.      Removing the last elements from the above labels for the case of singularity (As label names may be plural. Eg- Cells, muscles)
* Substring Checking:
1.      Checking if Label or Label author is present in Ubergraph Label or synonyms as a substring
2.      Checking if Ubergraph Label or Synonym is present in Cell Labels or Label authors as a substring
* For all these cases, we match and return all the parent labels associated with it.
### Cases to match Parent Labels with Azimuth/ASCT+B:
* Matching Parent Labels by direct and substring method and return the parent labels that have been matched for human verification.
* The unmatched labels are also sent for verification.
