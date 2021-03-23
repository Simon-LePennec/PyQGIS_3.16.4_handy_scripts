# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

import qgis
import processing
from qgis.processing import alg
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
import os

#About the alg decorator: https://docs.qgis.org/3.16/en/docs/user_manual/processing/scripts.html#the-alg-decorator
@alg(name='save_in_2154_shapefile', label='Reproject in 2154 and save layer as shapefile with _2154 suffix',
     group='General', group_label='General')
@alg.input(type=alg.SOURCE, name='INPUT', label='Input vector layer')
@alg.input(type=alg.VECTOR_LAYER_DEST, name='REPROJECT_OUTPUT', label='reprojected layer')


def savein2154shapefile(instance, parameters, context, feedback, inputs):
    """
    Reproject input in 2154 and save output as a shapefile with _2154 suffix, in the input's folder.
    You don't need to select output location.
    The purpose of this is to save time while working on webmapping with french data, because reprojections are pretty frequent.
    """

    input = instance.parameterDefinition('INPUT').valueAsPythonString(parameters['INPUT'], context)
    
    #Get the path
    #input_layer_path = str(input).split("'")[1]
    #output_layer_path = input_layer_path[:-4]+'_2154.shp'
    #input_layer = QgsVectorLayer(input_layer_path, 'input_layer', 'ogr')
    
    #Fancy way to get the path
    input_layer_path = str(input).split("'")[1]
    #input_layer_path = input_layer.dataProvider().dataSourceUri().split("'")[1]
    (directory,filename) = os.path.split(input_layer_path)
    new_filename = filename.split("'")[0][:-4]+'_2154.shp'
    output_layer_path = os.path.join(directory,new_filename).replace("\\", "/")
    
    #Reproject layer
    if feedback.isCanceled():
        return {}
    reprojected_layer = processing.run('native:reprojectlayer',
                               {'INPUT': parameters['INPUT'],
                                'TARGET_CRS': 'EPSG:2154',
                                'OPERATION': None,
                                'OUTPUT': new_filename 
                                #About output parameter: https://gis.stackexchange.com/a/295444/95584
                                },
                               is_child_algorithm=True,
                               context=context,
                               feedback=feedback
    )

    layer = QgsVectorLayer(reprojected_layer['OUTPUT'], 'reprojected_layer', 'ogr')

    #Options and save layer
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.fileEncoding = "UTF-8"
    options.driverName = "ESRI Shapefile"
    QgsVectorFileWriter.writeAsVectorFormatV2(
        layer,
        output_layer_path,
        QgsCoordinateTransformContext(),
        options
    )