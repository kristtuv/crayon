#
# util.py
# miscellaneous utility functions for other modules
#
# Copyright (c) 2018 Wesley Reinhart.
# This file is part of the crayon project, released under the Modified BSD License.

from __future__ import print_function

import numpy as np

def rotate(coords,axis,turns):
    R""" rotate 3D color coordinates along one of the three axes
         (must be limited like this to hold coordinates inside unit cube)

    Args:
        coords (array): `Nx3` array containing coordinates
        axis (int): axis to rotate around, specified as column (0=x,1=y,2=z)
        turns (int): number of 90-degree turns along the axis

    Returns:
        rcoords (array): `Nx3` array containing rotated coordinates
    """
    theta = int(turns) * 0.5 * np.pi
    R = []
    R.append( np.array([[1, 0,              0],
                        [0, np.cos(theta), -np.sin(theta)],
                        [0, np.sin(theta),  np.cos(theta)]]) )
    R.append( np.array([[ np.cos(theta), 0, np.sin(theta)],
                        [ 0,             1, 0],
                        [-np.sin(theta), 0, np.cos(theta)]]) )
    R.append( np.array([[np.cos(theta), -np.sin(theta), 0],
                        [np.sin(theta),  np.cos(theta), 0],
                        [0,              0,             1]]) )
    t = 0.5*np.ones(3)
    rcoords = t+np.matmul(coords-t,R[axis])
    return rcoords

def rankTransform(R):
    R""" transforms each column to provide uniform distribution over (0,1)

    Args:
        R (array): coordinates

    Returns:
        T (array): transformed coordinates
    """
    # transform data to uniform distribution
    T = np.zeros(R.shape)*np.nan
    # transform each remaining eigenvector to yield a uniform distribution
    for i in range(R.shape[1]):
        r = R[:,i]
        idx = np.argsort(r[r==r])
        rs = r[r==r][idx]
        x = np.linspace(0.,1.,len(rs))
        T[:,i] = np.interp(r,rs,x)
    nan_idx = np.argwhere(np.isnan(T[:,-1])).flatten()
    T[nan_idx,:] = 1.
    return T
