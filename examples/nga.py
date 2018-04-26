from __future__ import print_function
import sys

import numpy as np

sys.path.append('/Users/wfr/code/crayon')
sys.path.append('/Users/wfr/code/DiffusionMap/build')
import crayon

def readXYZ(filename):
    # read values from file
    with open(filename,'r') as config:
        lines = config.readlines()
    N = int(lines[0])
    if 'Lattice=' in lines[1]:
        box = np.asarray([float(x) for x in lines[1].replace('Lattice=','').replace('"','').split()[::4]])
    elif len(lines[1].split) == 3:
        box = np.asarray([float(x) for x in lines[1].split()])
    else:
        raise RuntimeError('unexpected box format in file %s'%filename)
    xyz = np.zeros((N,3))
    for i, l in enumerate(lines[2:]):
        xyz[i,:] = [float(x) for x in l.split()[1:]]
    return xyz, box

# snapshots to analyze
filenames = ['bcc.xyz','fcc.xyz','hcp.xyz','liquid.xyz']

# build neighbor list with a Voronoi construction
#   (or equivalenty Delaunay triangulation)
nl = crayon.neighborlist.Voronoi()

# use one neighbor shell for neighborhood graphs
traj = crayon.nga.Ensemble()

# read snapshots and build neighborhoods in parallel
local_filenames = crayon.parallel.partition(filenames)
for f in local_filenames:
    print('rank %d analyzing %s'%(traj.rank,f))
    xyz, box = readXYZ(f)
    snap = crayon.nga.Snapshot(xyz=xyz,box=box,nl=nl,pbc='xyz')
    traj.insert(f,snap)

# merge trajectories from different ranks
traj.collect()

# define landmarks as signatures with large clusters
traj.prune(mode='clustersize',min_freq=3)

# compute distances between neighborhood graphs
traj.computeDists()

# take distances to power of 0.5 to exaggerate polymorphs
traj.dmap.alpha = 0.33

# build diffusion map from distance matrix
traj.buildDMap()

# write color maps for visualization in Ovito or VMD
traj.writeColors()

# create a "snapshot" of the manifold for easy visualization
traj.makeSnapshot('manifold.xyz')
