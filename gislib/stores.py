# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import math

from osgeo import gdal
from osgeo import gdal_array
from osgeo import ogr

import numpy as np

from gislib import projections
from gislib import rasters
from gislib import vectors

OGR_MEM_DRIVER = ogr.GetDriverByName(b'Memory')


class BaseStore(object):
    """
    Base class for anything that has a warpinto method.
    """
    def get_data(self, wkt, crs, size=None):
        """
        Generalized data extraction from store interfaces.
        """
        wkb = ogr.CreateGeometryFromWkt(wkt)
        handler = self.HANDLERS[wkb.GetGeometryType()]
        return handler(self, wkb, crs, size=size)

    def get_data_for_polygon(self, wkb, crs, size):
        """
        Return a numpy array for the data.
        """
        # Quick out if polygon bounds match polygon
        geometry = vectors.Geometry(wkb)
        envelope = geometry.envelope
        extent = geometry.extent
        nodatavalue = self.info['nodatavalue']
        datatype = self.info['datatype']

        # Initialize resulting array to nodatavalue
        array = np.ones(
            (1, size[1], size[0]),
            dtype=gdal_array.flip_code(datatype),
        ) * nodatavalue

        # Create dataset and use it to retrieve data from the store
        dataset = rasters.array2dataset(array=array, extent=extent, crs=crs)
        self.warpinto(dataset)
        dataset.FlushCache()

        # Cut when necessary
        if not envelope.Equals(wkb):
            source = OGR_MEM_DRIVER.CreateDataSource('')
            sr = projections.get_spatial_reference(crs)
            layer = source.CreateLayer(b'', sr)
            defn = layer.GetLayerDefn()
            feature = ogr.Feature(defn)
            feature.SetGeometry(wkb)
            layer.CreateFeature(feature)
            gdal.RasterizeLayer(dataset, (1,), layer,
                                burn_values=(nodatavalue,))
            dataset.FlushCache()

        return np.ma.masked_equal(array, nodatavalue, copy=False)

    def get_data_for_linestring(self, wkb, crs, size):
        """ Profile code. """
        # Consider an envelope slightly larger than the lines envelope.
        length = wkb.Length()
        geometry = vectors.Geometry(wkb.Buffer(length / 100))
        envelope = geometry.envelope
        extent = geometry.extent
        span = geometry.size

        # Now, based on size and span, determine optimal dataset layout.
        cellsize = length / size
        gridsize = tuple(int(math.ceil(s / cellsize)) for s in span)
        x1, y1, x2, y2 = extent

        # Determine indices for one point per pixel on the line
        wkbpoints = wkb.ExportToWkb()[9:]
        vertices = np.fromstring(wkbpoints).byteswap().reshape(-1, 2)
        magicline = vectors.MagicLine(vertices).pixelize(cellsize)
        origin = np.array([x1, y2])
        points = magicline.centers
        indices = tuple(np.uint64(
            (points - origin) / cellsize * np.array([1, -1]),
        ).transpose())[::-1]

        # Get the values from the array
        values = self.get_data_for_polygon(crs=crs,
                                           wkb=envelope,
                                           size=gridsize)[0][indices]

        # make array with distance from origin (x values for graph)
        magnitudes = vectors.magnitude(magicline.vectors)
        distances = magnitudes.cumsum() - magnitudes[0] / 2

        return distances, values

    def get_data_for_point(self, wkb, crs, size):
        pass

    HANDLERS = {
        ogr.wkbPolygon: get_data_for_polygon,
        ogr.wkbLineString: get_data_for_linestring,
        ogr.wkbPoint: get_data_for_point,
    }


class MultiStore(BaseStore):
    """ Store wrapper for data extraction from a list of stores. """
    def __init__(self, stores):
        self.stores = stores

    @property
    def info(self):
        """ Return store info. """
        return self.stores[0].info

    def warpinto(self, dataset):
        """ Multistore version of warpinto. """
        for store in self.stores:
            store.warpinto(dataset)
