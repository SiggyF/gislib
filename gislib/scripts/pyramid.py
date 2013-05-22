# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import argparse
import logging

from osgeo import gdal

from gislib import raster

description = """
    Commandline tool for working with nens/gislib pyramid datasets.
"""

logging.root.level = logging.DEBUG

def get_parser():
    """ Return argument parser. """
    parser = argparse.ArgumentParser(
        description=description
    )
    parser.add_argument('sourcepath', metavar='SOURCE')
    parser.add_argument('targetpath', metavar='TARGET')
    parser.add_argument('-of', '--output-format', 
                        metavar='FORMAT', dest='outputformat',
                        choices=['pyramid', 'gtiff'])
    return parser


def pyramid(sourcepath, targetpath, outputformat):
    """ Do something spectacular. """
    source = gdal.Open(sourcepath)
    pyramid = raster.Pyramid(targetpath)
    pyramid.add(source)

def main():
    """ Call command with args from parser. """
    pyramid(**vars(get_parser().parse_args()))
