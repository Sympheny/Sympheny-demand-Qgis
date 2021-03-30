# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SymphenyDemands
                                 A QGIS plugin
 Generate demand profiles of the selected districts ready for Sympheny
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-11-05
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Urban Sympheny AG
        email                : carlos.pacheco@sympheny.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import QgsProject, Qgis, QgsMessageLog, QgsApplication
import pandas as pd
#from qgis.gui import QgisInterface
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Sympheny_demands_dialog import SymphenyDemandsDialog
import os.path, os
import pathlib, sys
import pip

class SymphenyDemands:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        #self.installer_func()
        #self.Copy_Xlsxmodule()

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SymphenyDemands_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&SymphenyDemands')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('SymphenyDemands', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Sympheny_demands/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Generate demand profiles'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&SymphenyDemands'),
                action)
            self.iface.removeToolBarIcon(action)


    def select_output_file(self):

        filename = QFileDialog.getExistingDirectory(self.dlg, "Select destination folder ",os.getcwd())
        self.dlg.lineOutFolder.setText(filename)

    def Getbuildingcodes(self, GisdemandDF):
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1121,1122,1130,1212,1275],'1 MFH')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1110],'2 EFH')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1220,1241,1274],'3 Verwaltung')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1263],'4 Schule')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1230],'5 Verkauf')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1231],'6 Restaurant')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1261,1262,1272,1273],'7 Versammlung')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1264],'8 Spital')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1251],'9 Industrie')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1242,1252,1271,1276,1277,1278],'10 Lager')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1265],'11 Sportbau')
        GisdemandDF['GKAT'] = GisdemandDF['GKAT'].replace([1211],'13 Hotel')
        #print (GisdemandDF)
        return GisdemandDF
    
    def run(self):
        """Run method that performs all the real work"""
        
        global output_file
        #print (sys.exec_prefix)
        #print (os.path.dirname(__file__))

        #import xlsxwriter
        #from .lib import xlsxwriter

        def writeexcel(df, dm, selectedfieldname, output_file):
            #try:
            output_file = output_file + "/Demand_" + dm + "_" + selectedfieldname + "_kWh.xls"
            writer = pd.ExcelWriter(output_file)  # pylint: disable=abstract-class-instantiated
            df.to_excel(writer, index= True, header= False, sheet_name='demand')  
            writer.save()
            return True
            #except:
            #return False
            #Qnormaldf

        # Create the dialog with elements (after tranxlslation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = SymphenyDemandsDialog()

            self.dlg.lineOutFolder.setText(os.path.expanduser('~/Documents'))
            self.dlg.pushButton.clicked.connect(self.select_output_file)

        # Active layer (The layer we want is GKAT)
        actvlayer = self.iface.activeLayer()
        #try:

        #Features are the Buildings (X,Y Points) inside a layer
        selected_buildings = actvlayer.selectedFeatures()
        if not len(selected_buildings) > 0:
            QMessageBox.warning(None, "No Building selection", "Please select at least one building")
            self.dlg.parent().close()

        # Fetch the currently loaded layers
        #layers = QgsProject.instance().layerTreeRoot().children()
        # Clear the contents of the comboBox from previous runs
        self.dlg.comboBox_heat.clear()
        self.dlg.comboBox_dhw.clear()
        self.dlg.comboBox_cool.clear()
        self.dlg.comboBox_elec.clear()


        # Populate the comboBox with names of all the field in the layer
        fieldnames = [None] +  [field.name() for field in actvlayer.fields()]
        #print (fieldnames)
        # fieldnames = ['X', 'Y', 'EGID', 'Baujahr', 'GKAT', 'Energieträger Qh','Energieträger WW', 
        # 'Heizen', 'Kühlen', 'Warmwasser', 'Qe GIS', 'Qe IBC', 'Gas GIS', 'Gas IBC', 
        # 't CO2 / Gebäude', 'EBF']
        self.dlg.comboBox_heat.addItems(fieldnames)
        self.dlg.comboBox_dhw.addItems(fieldnames)
        self.dlg.comboBox_cool.addItems(fieldnames)
        self.dlg.comboBox_elec.addItems(fieldnames)

        # show the QT dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()

        # Check that at least 1 combobox is != None
        combox = False
        for cm in [self.dlg.comboBox_heat, self.dlg.comboBox_dhw, self.dlg.comboBox_cool, self.dlg.comboBox_elec]:
            if fieldnames[cm.currentIndex()] is not None:
                combox = True
        if not combox:
            QMessageBox.warning(None, "Attributes selection", "Please select at least one attribute")
            result = self.dlg.exec_()

        # See if OK was pressed
        demandict = {'Heating':'Qh,norm', 'Domestic Hot Water':'Qww,norm', 'Cooling':'Qk,norm', 'Electricity': 'Qe,norm'}
        GisdemandBuildings = pd.DataFrame()
        selectedFieldsnam = []
        if result:
            for cmbx, dm in zip([self.dlg.comboBox_heat, self.dlg.comboBox_dhw, self.dlg.comboBox_cool, self.dlg.comboBox_elec], demandict):
                selectedFieldIndex = cmbx.currentIndex()
                selectedfieldname = fieldnames[selectedFieldIndex]

                if selectedfieldname is not None:

                    selectedFieldsnam.append(selectedfieldname) # List of field names to be used in summary Excel table
                    
                    # Create dict for excel
                    columns = ['EGID'] + ['GKAT'] + [selectedfieldname] + ['EBF']
                    rows = {c:[] for c in columns}

                    output_file = self.dlg.lineOutFolder.text()
                    #with open(filename, 'w') as output_file:

                    flag = False
                    for bi in selected_buildings:
                        fields = bi.fields()
                        for f in fields:
                            if f.name() == 'EBF':
                                #print (f.name(), f)
                                rows['EBF'].append(bi['EBF'])
                            if f.name() == 'EGID':
                                #print (f.name(), f)
                                rows['EGID'].append(bi['EGID'])
                            if f.name() == 'GKAT':
                                #print (f.name(), f)
                                flag = True
                                rows['GKAT'].append(bi['GKAT'])
                            if f.name() == selectedfieldname:
                                #print (selectedfieldname, bi[selectedfieldname])
                                try:
                                    value = float(bi[selectedfieldname])
                                except ValueError as e:
                                    QMessageBox.warning(None, "Attributes selected", "The attributes selected in some buildings are not numeric. Please check this again by clicking in 'Open Atribute Table'")
                                    self.dlg.parent().close()
                                rows[str(selectedfieldname)].append(value)
                    if not flag:
                        QMessageBox.warning(None, "Building Category problem", "It seems that the buildings selected don't have a 'GKAT' attribute with a numeric category assigned.")
                        self.dlg.parent().close()                       

                    # Get demand df with building codes
                    GisdemandDF = pd.DataFrame(rows, columns=columns)
                    GisdemandDF = self.Getbuildingcodes(GisdemandDF)
                    GisdemandBuildings = pd.concat([GisdemandBuildings, GisdemandDF], axis=1)

                    GisdemandDF = GisdemandDF.groupby("GKAT").sum()

                    # READ EXCEL WITH NORMALIZED DEMANDS
                    Input_file = QgsApplication.qgisSettingsDirPath() + "/" + "python/plugins/Sympheny-demand-Qgis-main/Normvalues.xlsx"
                    #QMessageBox.warning(None, "Attributes selection", str(Input_file))
                
                    # a dictionary is created with each df
                    Qnormaldf = pd.read_excel(Input_file, sheet_name=None)
                    print ("Qnormaldf --->", Qnormaldf)
                    # create df for hourly data
                    #Qhourdf = pd.DataFrame(columns = ['Qh/ww,eff','Qh,eff','Qww,eff','Qk,eff','Qe/m','effQe,eff','Qm,eff'])

                    # for each type of building group a Qhourdf is generated
                    demanddf = []
                    for bi in GisdemandDF.index:
                        buidlingsdf = Qnormaldf[bi][demandict[dm]] * GisdemandDF.loc[[bi],[selectedfieldname]].values[0][0]
                        #print (GisdemandDF.loc[[bi],['Heizen']].values[0][0])
                        demanddf.append(buidlingsdf)
                    
                    # sum demand of all buildings for the corresponding EC
                    result = pd.concat(demanddf, axis=1, sort=False)
                    resultsum = result.sum(axis=1)
                    df = resultsum.to_frame()
                    df.index = pd.RangeIndex(start = 1, stop=8761)

                    if not writeexcel(df,dm,selectedfieldname, output_file):
                        QMessageBox.warning(None, "Excel write error", 'An error ocurred while generating the Excel demand profile for {}' .format(dm))



            # Read surface and write energy intensity per building
            GisdemandBuildings = GisdemandBuildings.loc[:,~GisdemandBuildings.columns.duplicated(keep='first')]

            # Move column EBF at the end of the dataframe
            cols_at_end = ['EBF']
            GisdemandBuildings = GisdemandBuildings[[c for c in GisdemandBuildings if c not in cols_at_end]  +  [c for c in cols_at_end if c in GisdemandBuildings]]
            GisdemandBuildings = GisdemandBuildings.set_index('EGID')
            GisdemandBuildings = GisdemandBuildings.sort_values(by=['GKAT'])
            print ("GisdemandBuildings ------->", GisdemandBuildings)

            GisdemandCats = GisdemandBuildings.groupby("GKAT").sum()
            GisdemandCatsSum = GisdemandCats.sum().to_frame().T
            GisdemandCatsSum.index = ["TOTAL"]
            #print ("GisdemandCatsSum ------->", GisdemandCatsSum)

            for f in selectedFieldsnam:
                #print ("field name ----", f)
                GisdemandBuildings[f'Energy Int {f} [kWh/m2]'] = (GisdemandBuildings[f] / GisdemandBuildings["EBF"]).round(1) # For each type of demand
                GisdemandCats[f'Energy Int {f} [kWh/m2]'] = (GisdemandCats[f] / GisdemandCats["EBF"]).round(1) # For each type of demand
                GisdemandCatsSum[f'Energy Int {f} [kWh/m2]'] = (GisdemandCatsSum[f] / GisdemandCatsSum["EBF"]).round(1) # For each type of demand

            GisdemandCats = GisdemandCats.append(GisdemandCatsSum)

            # Write Excel of Summary of selected buildings
            output_file = output_file + "/Summary_SelectedBuildings.xls"
            with pd.ExcelWriter(output_file) as writer:
                GisdemandBuildings.to_excel(writer, index= True, header= True, sheet_name='Summary_Selected_Buildings')
                GisdemandCats.to_excel(writer, index= True, header= True, sheet_name='Summary_Building_Categories')
                writer.save()


            if writer:
                self.iface.messageBar().pushMessage(
                "Success", "Excel sheets with demands and a Summary Excel sheet of buildings were written in: " + output_file,
                level=Qgis.Success, duration=3)

