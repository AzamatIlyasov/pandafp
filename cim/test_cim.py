# from cimpyorm import datasets
# db_session, model = datasets.ENTSOE_FullGrid()
# db_session, model = datasets.ENTSOE_MiniBB()    # The Bus-Branch Model version
# db_session, model = datasets.ENTSOE_MiniNB()    # The Node-Breaker Model version

# #path_to_db = 
# #cimpyorm.load(path_to_db, echo=False)

import logging
import cimpy
from pathlib import Path

#logging.basicConfig(filename='importCIGREMV.log', level=logging.INFO, filemode='w')

#cimpy.import_example()
#example = Path('.').resolve()
#sample_folder = example / 'examples' / 'sampledata' / 'CIGRE_MV'

#sample_files = sample_folder.glob('*.xml')

xml_files = ["C:\FILES\PROJECTS\pandafp\cim\SmallGridTestConfiguration_EQ_BD_v3.0.0.xml", "C:\FILES\PROJECTS\pandafp\cim\SmallGridTestConfiguration_TP_BD_v3.0.0.xml"]
#for file in sample_folder.glob('*.xml'):
#    xml_files.append(str(file.absolute()))

cimpy.cimimport.cim_import(xml_files, "cgmes_v2_4_15")

#https://acs.pages.rwth-aachen.de/public/cim/cimpy/Install.html
#https://github.com/sogno-platform/cimpy

