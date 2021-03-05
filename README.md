# continuous-viewscape-modeling
Scripts for modeling spatially continuous viewscapes.

Basic workflow assuming data is prepared in GRASS location and computational region is set:

1. run generate_jobs to create regular grid and generate file with r.viewshed commands, jobs.txt then looks like:

```
grass72 -c grassdata/sonoita/temp_1 --exec python scripts/single_viewshed.py output=out_1.txt coord=518205,3485625 --o && rm -r grassdata/sonoita/temp_1
grass72 -c grassdata/sonoita/temp_2 --exec python scripts/single_viewshed.py output=out_2.txt coord=518235,3485625 --o && rm -r grassdata/sonoita/temp_2
grass72 -c grassdata/sonoita/temp_3 --exec python scripts/single_viewshed.py output=out_3.txt coord=518265,3485625 --o && rm -r grassdata/sonoita/temp_3
...
```
2. run each viewshed in parallel using GNU Parallel:

```
parallel < jobs.txt
```

3. merge the individual output files with merge.py or with:

```
find . -name "out_*.txt" | xargs cat >> all.csv
```
4. Create continuous raster with postprocess.sh

## other useful bash commands
Sort by first numerical column

```
sort -k1 -n -t, all.csv > all_sorted.csv
```
