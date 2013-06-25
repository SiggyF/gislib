# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.

"""
A structure defines the combination of dimensions and datacontent for
a datastore.

The dimensions and data are interweaved, since NED dimensions need a
dimension parameter in the basic datastructure.
"""

class Structure(object):
    def __init__(self, dimensions, chunkshape, dtype, nodatavalue):
        self.nodatavalue = nodatavalue  # Also used to identify NED removals.
        self.dimensions = dimensions
        self.chunkshape = chunkshape
        self.dtype = dtype  # Any pickleable numpy dtype object will do.
