#!/usr/bin/env python

import os
import grass.script as gscript

location = '/share/mitasova/akratoc/grassdata/viewscapes_grass/'
viewshed_script = '~/continuous-viewscape-modeling/single_viewshed.py'
results_dir = '/share/mitasova/akratoc/viewscapes/out/'
vector = 'survival_new'
columns = "id,x_1,y"
jobs_file = "/home/akratoc/continuous-viewscape-modeling/house_jobs_hpc.txt"

template = 'grass --tmp-mapset {location} --exec python  {viewshed_script} output={results_dir}{out} input=dem input_dsm=dsm dem_buffer=10 sample_continuous=tri sample_categorical=lc1992,lc2001,lc2006,lc2011,lc2016,neighbors1,neighbors2,neighbors3,neighbors4,neighbors5,neighbors6,fires1,fires2,fires3,fires4,fires5,fires6 max_distance=10000 observer_elevation=3 coordinates={x},{y} view_id={pid} memory=40000 --o \n'

out = gscript.read_command('v.db.select', map=vector, column=columns, flags='c').strip()
with open(jobs_file, "w") as f:
    for line in out.splitlines():
        id, x, y = line.split('|')
        f.write(template.format(x=x, y=y, pid=id, out='out_' + id + '.txt',
                                location=location, viewshed_script=viewshed_script, results_dir=results_dir))
