#!/usr/bin/env python

import os
import grass.script as gscript

# set computational region beforehand
grid = 'grid'
       
gscript.run_command('v.mkgrid', type='point', map=grid, overwrite=True)
print gscript.vector_info(grid)['points']
gscript.run_command('v.out.ascii', input=grid, sep='comma', output='grid.txt', overwrite=True)

template = 'grass72 -c grassdata/sonoita/{mapset} --exec python scripts/single_viewshed.py output={out} coord={x},{y} --o && rm -r grassdata/sonoita/{mapset}\n'

with open("grid.txt") as f:
    with open("jobs.txt", "w") as f1:
        for line in f:
            x, y, cat = line.strip().split(',')
            f1.write(template.format(mapset='temp_' + cat, x=x, y=y, out='out_' + cat + '.txt')) 
