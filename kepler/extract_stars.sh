#!/bin/bash

cat /opt/data/csv/phl_hec_all_kepler.csv | tail -n +2  | awk -F, -v OFS=',' '{print $34, $35, $36, $37, $38, $39, $40, $41, $42, $43, $44, $45, $46, $47, $48, $49, $50, $51, $52, $53, $54}'  | sort --field-separator=, -u -k1,1 
