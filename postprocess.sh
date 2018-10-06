#!/usr/bin/env bash 
g.region -p res=30 `r.in.xyz inp=all.csv out=total meth=mean z=3 sep=comma -sg --o`

C=2
for I in view_size ndvi_min ndvi_max ndvi_range ndvi_mean ndvi_stddev ndvi_sum tri_min tri_max tri_range tri_mean tri_stddev tri_sum houses_min houses_max houses_range houses_mean houses_stddev houses_sum
do
let "C = 1 + C"
    r.in.xyz inp=all.csv out=${I} meth=mean z=$C sep=comma --o
    r.out.gdal input=${I} output=${I}.tif createopt="PROFILE=GeoTIFF" type=Float32 --o
done

