# -*- coding: utf-8 -*-

'''
/***************************************************************************
 Offline-MapMatching
                                 A QGIS plugin
 desciption of the plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-08-08
        copyright            : (C) 2018 by Christoph Jung
        email                : jagodki.cj@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''

__author__ = 'Christoph Jung'
__date__ = '2018-08-08'
__copyright__ = '(C) 2018 by Christoph Jung'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtGui import QIcon
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterField,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsFields)
from ..mm.map_matcher import MapMatcher
import time, os.path


class OfflineMapMatchingAlgorithm(QgsProcessingAlgorithm):
    '''
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    '''

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    NETWORK = 'NETWORK'
    TRAJECTORY = 'TRAJECTORY'
    TRAJECTORY_ID = 'TRAJECTORY_ID'
    CRS = 'CRS'
    SIGMA = 'SIGMA'
    MY = 'MY'
    BETA = 'BETA'
    MAX_SEARCH_DISTANCE = 'MAX_SEARCH_DISTANCE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config):
        '''
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        '''
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.NETWORK,
                self.tr('Network layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.TRAJECTORY,
                self.tr('Trajectory layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.TRAJECTORY_ID,
                self.tr('Trajectory ID'),
                parentLayerParameterName=self.TRAJECTORY,
                type=QgsProcessingParameterField.Any
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.CRS,
                self.tr('CRS of the Output layer (EPSG)')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIGMA,
                self.tr('Standard Deviation [m]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=50.0,
                minValue=0.0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MY,
                self.tr('Expected Value [m]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0,
                minValue=0.0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.BETA,
                self.tr('Mean Difference between Distances [m]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=30.0,
                minValue=0.0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAX_SEARCH_DISTANCE,
                self.tr('Maximum Search Distance [m]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0,
                minValue=0.0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        '''
        Here is where the processing itself takes place.
        '''
        start_time = time.time()
        mm = MapMatcher()
        
        #create a QgsFields-object
        attrs = mm.defineAttributes()
        fields = QgsFields()
        for field in attrs:
            fields.append(field)
        
        #extract all parameters
        network_layer = self.parameterAsVectorLayer(
            parameters,
            self.NETWORK,
            context
        )
        
        trajectory_layer = self.parameterAsVectorLayer(
            parameters,
            self.TRAJECTORY,
            context
        )
        
        trajectory_id = self.parameterAsString(
            parameters,
            self.TRAJECTORY_ID,
            context
        )
        
        crs = self.parameterAsString(
            parameters,
            self.CRS,
            context
        )
        
        sigma = self.parameterAsDouble(
            parameters,
            self.SIGMA,
            context
        )
        
        my = self.parameterAsDouble(
            parameters,
            self.MY,
            context
        )
        
        beta = self.parameterAsDouble(
            parameters,
            self.BETA,
            context
        )
        
        max_search_distance = self.parameterAsDouble(
            parameters,
            self.MAX_SEARCH_DISTANCE,
            context
        )
        
        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.LineString,
            QgsCoordinateReferenceSystem('EPSG:' + crs)
        )
        
        error_code = mm.startViterbiMatchingProcessing(trajectory_layer,
                                                       network_layer,
                                                       trajectory_id,
                                                       sigma,
                                                       my,
                                                       beta,
                                                       max_search_distance,
                                                       sink,
                                                       feedback)
        
        return {'OUTPUT': dest_id,
                'ERROR_CODE': error_code,
                'COMPUTATION_TIME': str(round(time.time() - start_time, 2))}

    def name(self):
        '''
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'match_trajectory'
    
    def helpUrl(self):
        '''
        Returns the URL for the help document, if a help document does exist.
        '''
        dir = os.path.dirname(__file__)
        file = os.path.abspath(os.path.join(dir, '..', 'help_docs', 'help.html'))
        if not os.path.exists(file):
            return ''
        return QUrl.fromLocalFile(file).toString(QUrl.FullyEncoded)

    def shortHelpString(self):
        '''Returns the text for the help widget, if a help document does exist.'''
        dir = os.path.dirname(__file__)
        file = os.path.abspath(os.path.join(dir, '..', 'help_docs', 'help_processing_match_trajectory.html'))
        if not os.path.exists(file):
            return ''
        with open(file) as helpf:
            help=helpf.read()
        return help
    
    def displayName(self):
        '''
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        '''
        return self.tr('Match Trajectory')

    def group(self):
        '''
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        '''
        return self.tr(self.groupId())
    
    def groupId(self):
        '''
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        '''
        return 'Matching'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return OfflineMapMatchingAlgorithm()

    def icon(self):
        return QIcon(':/plugins/offline_map_matching/icon.png')
