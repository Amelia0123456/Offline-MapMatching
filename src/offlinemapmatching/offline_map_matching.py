# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OfflineMapMatching
                                 A QGIS plugin
 a plugin to for map matching a trajetory using algirthms of viterbi and dijkstra
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-06-14
        git sha              : $Format:%H$
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
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.gui import QgsMessageBar
from qgis.core import QgsMessageLog
import time, traceback

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .offline_map_matching_dialog import OfflineMapMatchingDialog
import os.path

#import own classes
from .mm.map_matcher import MapMatcher


class OfflineMapMatching:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OfflineMapMatching_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = OfflineMapMatchingDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Offline-MapMatching')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'OfflineMapMatching')
        self.toolbar.setObjectName(u'OfflineMapMatching')
        
        #create additional instance vars
        self.map_matcher = MapMatcher()
        
        #connect slots and signals
        self.dlg.comboBox_trajectory.currentIndexChanged.connect(self.startPopulateFieldsComboBox)
        self.dlg.pushButton_start.clicked.connect(self.startMapMatching)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('OfflineMapMatching', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/offline_map_matching/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Offline-MapMatching'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Offline-MapMatching'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        #populate the comboboxes with the available layers
        self.populateComboBox("network")
        self.populateComboBox("trajectory")
        self.populateComboBox("fields")
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        #result = self.dlg.exec_()
        # See if OK was pressed
        #if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #pass
    
    def populateComboBox(self, type):
        """Populate the given combobox."""
        if type == "network":
            self.map_matcher.fillLayerComboBox(self.iface, self.dlg.comboBox_network, "LINESTRING")
        elif type == "trajectory":
            self.map_matcher.fillLayerComboBox(self.iface, self.dlg.comboBox_trajectory, "POINT")
        elif type == "fields":
            self.map_matcher.fillAttributeComboBox(self.dlg.comboBox_trajectoryID, self.dlg.comboBox_trajectory.currentText())

    def startPopulateFieldsComboBox(self):
        self.populateComboBox("fields")
    
    def startMapMatching(self):
        try:
            start_time = time.time()
            result = self.map_matcher.startViterbiMatching(
                          self.dlg.progressBar,
                          self.dlg.comboBox_trajectory.currentText(),
                          self.dlg.comboBox_network.currentText(),
                          self.dlg.comboBox_trajectoryID.currentText(),
                          self.dlg.doubleSpinBox_sigma.value(),
                          self.dlg.doubleSpinBox_my.value(),
                          self.dlg.doubleSpinBox_max.value(),
                          self.dlg.label_info,
                          self.dlg.lineEdit_crs.text())
            if result:
                self.iface.messageBar().pushMessage('Chainage finished ^o^ - time: ' + str(time.time() - start_time) + " sec", level=Qgis.Success, duration=60)
            
        except:
            QgsMessageLog.logMessage(traceback.print_exc(), level=Qgis.Critical)
            self.iface.messageBar().pushMessage('An error occured. Please look into the log and/or Python console for further information.', level=Qgis.Critical, duration=60)
