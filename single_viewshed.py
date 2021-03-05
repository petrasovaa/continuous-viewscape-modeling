#!/usr/bin/env python3

#%module
#% description: Compute viewshed and compute statistics about visible parts of sample layers
#% keyword: viewshed
#% keyword: geometry
#%end
#%option G_OPT_R_INPUT
#% key: input
#% description: Name of input elevation raster map
#%end
#%option G_OPT_M_COORDS
#% key: coordinates
#%end
#%option
#% key: view_id
#% type: integer
#% required: no
#% multiple: no
#% key_desc: value
#% description: View id
#%end
#%option
#% key: observer_elevation
#% type: double
#% required: no
#% multiple: no
#% key_desc: value
#% description: Viewing elevation above the ground
#% answer: 1.75
#%end
#%option
#% key: target_elevation
#% type: double
#% required: no
#% multiple: no
#% key_desc: value
#% description: Offset for target elevation above the ground
#% answer: 0.0
#%end
#%option
#% key: max_distance
#% type: double
#% required: yes
#% multiple: no
#% key_desc: value
#% description: Maximum visibility radius. By default infinity (-1)
#% answer: -1
#%end

#%option
#% key: direction
#% type: double
#% required: no
#% multiple: no
#% key_desc: value
#% description: Direction
#%end

#%option
#% key: angle
#% type: double
#% required: no
#% multiple: no
#% key_desc: value
#% description: Half angle of the horizontal view
#%end

#%option G_OPT_F_OUTPUT
#% key: output
#%end

#%option G_OPT_R_INPUTS
#% key: sample_continuous
#% required: no
#% description: Name of continuous raster maps to sample
#%end

#%option G_OPT_R_INPUTS
#% key: sample_categorical
#% required: no
#% description: Name of categorical raster maps to sample
#%end

#%flag
#% key: c
#% description: Print column headers
#%end

# %option
# % key: memory
# % type: integer
# % required: no
# % multiple: no
# % key_desc: value
# % description: Amount of memory to use in MB
# % answer: 500
# %end

import os
import grass.script as gs


def compute_direction(main_direction, half_angle):
    mina = main_direction - half_angle
    maxa = main_direction + half_angle
    if maxa > 360:
        maxa -= 360
    if mina < 0:
        mina += 360
    return mina, maxa


def main(elevation, coords, vid, observer_elevation, target_elevation,
         max_distance, direction, angle, output, sample_continuous, sample_categorical, header, memory):
    name = 'viewshed'
    gs.run_command('g.region', raster=elevation)
    gs.run_command('g.region', n=coords[1] + max_distance, s=coords[1] - max_distance,
                   e=coords[0] + max_distance, w=coords[0] - max_distance, align=elevation)
    region = gs.region()
    params = {}
    if max_distance:
        params['max_distance'] = max_distance
    if target_elevation:
        params['target_elevation'] = target_elevation
    if observer_elevation:
        params['observer_elevation'] = observer_elevation
    if direction:
        mina, maxa = compute_direction(float(direction), float(angle))
        params['direction_range'] = [mina, maxa]
    gs.run_command('r.viewshed', input=elevation, output=name,
                        coordinates=coords, flags='cb',
                        memory=memory, quiet=True, **params)
    
    
    # area
    cells = gs.parse_command('r.univar', map=name, flags='g', quiet=True)['sum']
    res = region['nsres']
    area = float(cells) * res * res
    # sampling
    results_continuous = []
    results_categorical = []

    for each in sample_continuous:
        results_continuous.append(gs.read_command('r.univar', map=each, zones=name, quiet=True, flags='t', separator='comma').strip().splitlines()[-1].split(','))
        
    gs.run_command('r.null', map=name, setnull=0)
    for each in sample_categorical:
        results_categorical.append(gs.read_command('r.univar', map=name, zones=each, quiet=True, flags='t', separator='comma').strip().splitlines()[1:])

    with open(output, 'w') as f:
        if header:
            if vid:
                f.write("view_id,")
            f.write("x,y,area")
            for each in results_continuous:
                for st in ('minim', 'maxim', 'range', 'mean', 'stddev', 'sum'):
                    f.write("," + each + "_" + st)
            for i, each in enumerate(results_categorical):
                all_cats = []
                for line in gs.read_command('r.category', map=sample_categorical[i], separator='comma').strip().splitlines():
                    all_cats.append(int(line.split(',')[0]))
                for c in all_cats:
                    f.write("," + each + "_" + str(c))
            f.write(os.linesep)

        if vid:
            f.write("%s," % vid)
        f.write("%.4f,%.4f,%.4f" % (coords[0], coords[1], area))
        for each in results_continuous:
            zone, label, non_null_cells, null_cells, minim, maxim, range_, mean, mean_of_abs, stddev, variance, coeff_var,  sum_, sum_abs = each
            if zone == '0':
                minim, maxim, range_, mean, stddev, sum_ = 0, 0, 0, 0, 0, 0
            f.write(",%.2f,%.2f,%.2f,%.2f,%.2f,%.2f" % (float(minim), float(maxim), float(range_), float(mean), float(stddev), float(sum_)))

        for i, each in enumerate(results_categorical):
            all_cats = []
            for line in gs.read_command('r.category', map=sample_categorical[i], separator='comma').strip().splitlines():
                all_cats.append(int(line.split(',')[0]))
            zones = {}
            for line in each:
                zone, label, non_null_cells, null_cells, minim, maxim, range_, mean, mean_of_abs, stddev, variance, coeff_var,  sum_, sum_abs = line.split(',')
                zones[int(zone)] = int(non_null_cells)
            for zone in all_cats:
                if zone in zones:
                    area = zones[zone] * res * res
                    f.write(",%.0f" % area)
                else:
                    f.write(",0")
        f.write(os.linesep)
    gs.run_command('g.remove', type='raster', name=[name], flags='f', quiet=True)


if __name__ == '__main__':
    options, flags = gs.parser()
    coords = options['coordinates'].split(',')
    sample_continuous = []
    if options['sample_continuous']:
        sample_continuous = options['sample_continuous'].split(',')
    sample_categorical = []
    if options['sample_categorical']:
        sample_categorical = options['sample_categorical'].split(',')
    main(elevation=options['input'],
         coords=(float(coords[0]), float(coords[1])),
         vid=options['view_id'],
         observer_elevation=options['observer_elevation'],
         target_elevation=options['target_elevation'],
         max_distance=float(options['max_distance']),
         direction=options['direction'],
         angle=options['angle'],
         output=options['output'],
         sample_continuous=sample_continuous,
         sample_categorical=sample_categorical,
         header=flags['c'],
         memory=options['memory'])

