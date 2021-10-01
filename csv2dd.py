# coding: utf-8

__Name__ = 'csv2dd'
__Comment__ = '''
Create dynamicData objects in FreeCAD from csv file.
It allows create several dynamicData objects in one click containing multiple variables per object
and naming the dynamicData objects different that "dd".
'''
__Author__ = "Daniel Pose. iinjdpa at gmail"
__Version__ = '0.2.1'
__Date__ = '2021-09-30'
__License__ = 'MIT'
__Web__ = ""
__Wiki__ = ""
__Icon__ = ''
__Help__ = ''
__Status__ = 'stable'
__Requires__ = 'Freecad >= 0.19'
__Communication__ = ''
__Files__ = ''

from PySide.QtGui import QMessageBox, QFileDialog

import FreeCAD as App
import FreeCADGui as Gui
import csv

propertyTypes =[
    "Acceleration",
    "Angle",
    "Area",
    "Bool",
    "Color",
    "Direction",
    "Distance",
    "File",
    "FileIncluded",
    "Float",
    "FloatConstraint",
    "FloatList",
    "Font",
    "Force",
    "Integer",
    "IntegerConstraint",
    "IntegerList",
    "Length",
    "Link",
    "LinkChild",
    "LinkGlobal",
    "LinkList",
    "LinkListChild",
    "LinkListGlobal",
    "LinkSubList",
#    "Material",
    "MaterialList",
    "Matrix",
    "Path",
    "Percent",
    "Placement",
    "PlacementLink",
    "Position",
    "Precision",
    "Pressure",
    "Quantity",
    "QuantityConstraint",
    "Speed",
    "String",
    "StringList",
    "Vector",
    "VectorList",
    "VectorDistance",
    "Volume"]

# Get path for FreeCAD macros
p=App.ParamGet("User parameter:BaseApp/Preferences/Macro")
macroPath = p.GetString("MacroPath")
file_path = os.path.join(macroPath,'./csv2dd.txt')


class csv2dd(object):
    def __init__(self):
        self.csvfile = ''
        self.data = []

    def get_csv(self):
        csv_path = ''
        # try:
        with open(file_path,'r') as f:
            csv_path = f.read()
            csv_path = csv_path.replace('\n','').strip()
        # except:
        #     pass
        if os.path.exists(csv_path):
            self.csvfile = csv_path
        else:
            self.csvfile = QFileDialog.getOpenFileName(None, 'Open csv file', '.','csv file(*.csv)')[0]
    
    def read_csv(self):
        with open(self.csvfile, newline='',encoding='utf-8') as f: # encoding='utf-8'
            reader = csv.reader(f)
            line_count = 0
            try:
                for row in reader:
                    if line_count == 0:
                        # Column titles
                        line_count += 1
                        continue
                    else:
                        dd_exists = False
                        for dd in self.data:
                            if dd['name'] == row[0]:
                                dd_exists = True
                                dd['variables'].append({         
                                'name':row[3],
                                'variableType':row[1],
                                'group':row[2],
                                'value':row[4].replace(",",'.').strip(),
                                'comment':row[5]
                                })
                        if not dd_exists:
                            self.data.append({'name':row[0],'variables':[]})
                            self.data[-1]['variables'].append({         
                                'name':row[3],
                                'variableType':row[1],
                                'group':row[2],
                                'value':row[4],
                                'comment':row[5]
                                })
            except:
                QMessageBox.critical(None, "Error","Error at csv reading. Try to save csv as utf-8")
        return
    
    def dd2FreeCAD(self):
        self.read_csv()
        objs = App.ActiveDocument.Objects
        objs_list = {}
        for obj in objs:
            if 'FeaturePython' in obj.TypeId:
                pp = getattr(obj,'DynamicData',False)
                if pp:
                    if pp[0] == 'Created with csv2dd macro':
                        objs_list[obj.Label] = obj
        dds_in_csv = []
        for dd in self.data:
            dds_in_csv.append(dd['name'])
            if dd['name'] in objs_list:
                odd = objs_list[dd['name']]
            else:
                odd = App.ActiveDocument.addObject("App::FeaturePython",dd['name'])
                setattr(odd.ViewObject,'DisplayMode',['0'])
                odd.touch()
                App.ActiveDocument.recompute()
                odd.addProperty("App::PropertyStringList","DynamicData").DynamicData=['Created with csv2dd macro']
                odd.touch()
                App.ActiveDocument.recompute()
            pp_list = odd.PropertiesList
            pp_list = [x for x in pp_list if x not in ['DynamicData', 'ExpressionEngine', 'Label', 'Label2', 'Proxy', 'Visibility']]
            vars_in_csv_dd = []
            for pp in dd['variables']:
                vars_in_csv_dd.append(pp['name'])
                if pp['name'] in pp_list:
                    op = getattr(odd,pp['name'])
                    App.ActiveDocument.openTransaction("modify Property")
                    op.Value = pp['value']
                    App.ActiveDocument.commitTransaction()
                    App.ActiveDocument.recompute()
                else:
                    if pp['variableType'] in propertyTypes:
                        App.ActiveDocument.openTransaction("dd Add Property")
                        op = odd.addProperty(
                            'App::Property'+pp['variableType'],
                            pp['name'],
                            pp['group'],
                            pp['comment']
                        )
                        opValue = getattr(odd,pp['name'])
                        opValue.Value = pp['value']
                        App.ActiveDocument.commitTransaction()
                        App.ActiveDocument.recompute()
                    else:
                        QMessageBox.critical(None, "Error",f"variable of type {pp['variableType']} not allowed!")
            for pp in pp_list:
                if not pp in vars_in_csv_dd:
                    App.ActiveDocument.openTransaction("remove Property")
                    odd.removeProperty(pp)
                    App.ActiveDocument.commitTransaction()
                    App.ActiveDocument.recompute()
        # Delete dynamicData not in csv
        for k,v in objs_list.items():
            if not k in dds_in_csv:
                App.ActiveDocument.removeObject(v.Name) 
        QMessageBox.information(None, "Ready","dynamicData objects and variables correctly generated and updated!")
        return

if __name__ == '__main__':
    oCsv2dd = csv2dd()
    oCsv2dd.get_csv()
    if oCsv2dd.csvfile != '':
        oCsv2dd.dd2FreeCAD()