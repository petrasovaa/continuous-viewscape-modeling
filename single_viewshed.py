#!/usr/bin/env python

#%module
#% description: viewshed
#% keyword: vector
#% keyword: geometry
#%end

#%option G_OPT_M_COORDS
#% key: coordinates
#%end

#%option
#% key: property_id
#% type: integer
#% required: no
#% multiple: no
#% key_desc: value
#% description: Property id
#%end

#%option G_OPT_F_OUTPUT
#% key: output
#%end

import os
import grass.script as gscript


def main(elevation, coords, output, pid, sample):
    limit = 10000
    name = 'viewshed'
    gscript.run_command('g.region', raster=elevation)
    gscript.run_command('g.region', n=coords[1] + limit, s=coords[1] - limit,
                         e=coords[0] + limit, w=coords[0] - limit, align=elevation)
    region = gscript.region()
    
    gscript.run_command('r.viewshed', input=elevation, output=name,
                        coordinates=coords, observer_elevation=3,# target_elevation=3,
                        max_distance=limit, flags='cb',
                        memory=25000, overwrite=True, quiet=True)
    
    # area
    cells = gscript.parse_command('r.univar', map=name, flags='g', quiet=True)['sum']
    res = region['nsres']
    area = float(cells) * res * res / 1000000
    # ndvi
    results = []
    # non_null_cells|null_cells|min|max|range|mean|mean_of_abs|stddev|variance|coeff_var|sum|sum_abs
    for each in sample:
        results.append(gscript.read_command('r.univar', map=each, zones=name, quiet=True, flags='t', separator='comma').strip().splitlines()[-1].split(','))

    with open(output, 'w') as f:
        if pid:
            f.write("%s,%.4f" % (pid, area))
        else:
            f.write("%.4f,%.4f,%.4f" % (coords[0], coords[1], area))
        for each in results:
            zone, label, non_null_cells, null_cells, minim, maxim, range_, mean, mean_of_abs, stddev, variance, coeff_var,  sum_, sum_abs = each
            if zone == '0':
                minim, maxim, range_, mean, stddev, sum_ = 0, 0, 0, 0, 0, 0
            f.write(",%.2f,%.2f,%.2f,%.2f,%.2f,%.2f" % (float(minim), float(maxim), float(range_), float(mean), float(stddev), float(sum_)))
        f.write("\n")
    gscript.run_command('g.remove', type='raster', name=[name], flags='f', quiet=True)


if __name__ == '__main__':
    options, flags = gscript.parser()
    pid = options['property_id']
    if not pid:
        pid = None
    coords = options['coordinates'].split(',')
    main(elevation='dem10',
         coords=(float(coords[0]), float(coords[1])),
         output=options['output'],
         pid = pid,
         sample=['ndvi', 'tri', 'real_houses'])

