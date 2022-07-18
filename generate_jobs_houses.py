#!/usr/bin/env python

import os
import grass.script as gscript

template = "grass72 -c grassdata/sonoita/{mapset} --exec python scripts/single_viewshed.py output={out} coord={x},{y} property_id={pid} --o && rm -r grassdata/sonoita/{mapset}\n"

out = gscript.read_command(
    "v.db.select", map="house_locations_utm", column="Id,x,y", flags="c"
).strip()
with open("house_jobs.txt", "w") as f:
    for line in out.splitlines():
        id, x, y = line.split("|")
        f.write(
            template.format(
                mapset="temp_" + id, x=x, y=y, pid=id, out="out_" + id + ".txt"
            )
        )
