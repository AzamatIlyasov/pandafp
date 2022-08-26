from flask import Flask, request
import sys


sys.path.append(r'C:\Program Files\DIgSILENT\PowerFactory 2021 SP3\Python\3.9')
import powerfactory as pf


app = Flask(__name__)


@app.route("/execute")
def execute():
    
  #get load flow object
    oLoadflow.Execute()

    result = {}
    grid = []

     #get the generators and their active/reactive power and loading
    Generators = power_factory_app.GetCalcRelevantObjects('*.ElmGenstat')  #'*.ElmSym')
    gen_attrs = ['loc_name', 'c:p', 'c:q', 'n:Ul:bus1', 'n:phiu:bus1', "outserv"]
    for gen in Generators: 
        grid_line = {}
        for attr in gen_attrs:
            # we do it because faceplate grid cannot work with ':' character 
            key = attr.replace(":", "_")
            grid_line[key] = getattr(gen, attr, -1)
            if key != "loc_name":
                grid_line[key] = round(grid_line[key], 2)
        grid.append(grid_line)
    result["generators"] = grid

    #get the lines
    grid = []
    Lines=power_factory_app.GetCalcRelevantObjects('*.ElmLne')
    lines_attr = ['loc_name', 'm:P:bus1', 'm:Q:bus1', 'n:Ul:bus1', 'n:Ul:bus2', 'n:u:bus1', 'n:u:bus2', "outserv"]
    for line in Lines: #loop through list
        grid_line = {}
        for attr in lines_attr:
            # we do it because faceplate grid cannot work with ':' character 
            key = attr.replace(":", "_")
            grid_line[key] = getattr(line, attr, -1)
            if key != "loc_name":
                grid_line[key] = round(grid_line[key], 2)
        grid.append(grid_line)
    result["lines"] = grid

    #get the buses
    grid = []
    buses_attr = ['loc_name', 'm:u1', 'm:Ul', 'm:phiu', "outserv"]
    Buses=power_factory_app.GetCalcRelevantObjects('*.ElmTerm')
    for bus in Buses: #loop through list
        grid_line = {}
        for attr in buses_attr:
            # we do it because faceplate grid cannot work with ':' character 
            key = attr.replace(":", "_")
            grid_line[key] = getattr(bus, attr, -1)
            if key != "loc_name":
                grid_line[key] = round(grid_line[key], 2)
        grid.append(grid_line)
    result["buses"] = grid

    #get the loads
    grid = []
    load_attr = ['loc_name', 'e:plini', 'e:qlini', 'r:bus1:r:cterm:e:loc_name', "outserv"]
    Loads = power_factory_app.GetCalcRelevantObjects("*.ElmLod")
    for load in Loads:
        grid_line = {}
        for attr in load_attr:
            # we do it because faceplate grid cannot work with ':' character 
            key = attr.replace(":", "_")
            grid_line[key] = getattr(load, attr, -1)
            if key != "loc_name" and key != 'r_bus1_r_cterm_e_loc_name':
                grid_line[key] = round(grid_line[key], 2)
        grid.append(grid_line)
    result["loads"] = grid

    return result
    
# data
# {
#     "generators": {
#         "G 02" : {"c:p" : 100, "c:q" : 123.213},
#         "G 010" : {"c:p" : 123}
#     },
#     "loads": {
#         "Load 04" : {"e:plini" : 100},
#         "Load 15" : {"e:plini" : 123, "e:qlini" : 662}
#     },
#     "buses": {
#         "Bus 10": {"m:Ul" : 123123}
#     },
#     "lines": {}
# }


@app.route("/setparams", methods=["POST"])
def setparams():
    mapping = {
        "generators" : '*.ElmGenstat',  #'*.ElmSym',
        "lines" : '*.ElmLne',
        "buses" : '*.ElmTerm',
        "loads" : "*.ElmLod"
    }
    data = request.json
    print(data)
    for item in data:
        if item not in mapping:
            continue
        mask = mapping[item]
        values = data[item]
        print("CYCLE START")
        print(f"table={item}")
        print(f"mask={mask}")
        print(f"values={values}")
        DataObjects = power_factory_app.GetCalcRelevantObjects(mask)
        for obj in DataObjects:
            loc_name = getattr(obj, "loc_name")
            print(loc_name)
            if loc_name in values:
                for key,value in values[loc_name].items():
                    # we do it because faceplate grid cannot work with ':' character 
                    key = key.replace("_", ":")
                    setattr(obj, key, value)
        print("CYCLE END")

    return {"result": "ok"}






if __name__ == "__main__":

      ## We do it here because powerfactory object cannot be accessed from external threads
    power_factory_app = pf.GetApplication()
    if power_factory_app is None:
        raise Exception('getting Powerfactory application failed')
    projName =    '39 Bus New England System'   #'CSPA_Model_(0806)'
   
    #НОРМ СХЕМА
    study_case = 'Study Case'
    #'1. Power Flow.IntCase'    
    
    #activate project
    project = power_factory_app.ActivateProject(projName)
    proj = power_factory_app.GetActiveProject()

    #get the study case folder and activate project
    oFolder_studycase = power_factory_app.GetProjectFolder('study')
    oCase = oFolder_studycase.GetContents(study_case)[0]
    oCase.Activate()

    oLoadflow = power_factory_app.GetFromStudyCase('ComLdf') 

    app.run(host='0.0.0.0', port=5000, threaded=False)
