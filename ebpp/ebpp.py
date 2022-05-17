import json
from logging.config import valid_ident
import os
import sys

import pandapower as pp
import pandapower.estimation as est

import pandas as pd
from flask import Flask, request
from dotenv import load_dotenv
from pandapower import LoadflowNotConverged

import utils
from errors import ConvError, InvalidError, JsonError, PPError


app = Flask(__name__)

# ERROR HANDLING

@app.errorhandler(InvalidError)
def invalid_error(error):
    """Replies with an invalid error message"""
    return json.dumps(error.to_dict())

@app.errorhandler(JsonError)
def json_error(error):
    """Replies with an json error message"""
    return json.dumps(error.to_dict())

@app.errorhandler(PPError)
def pp_error(error):
    """Replies with a pandapower error message"""
    return json.dumps(error.to_dict())

@app.errorhandler(ConvError)
def conv_error(error):
    """Reples with a pandapower convergence error"""
    return json.dumps(error.to_dict())

# API ENTRY POINTS

@app.route("/")
def index():
    return "Welcome to Electric Blocks Panda Power. Please visit <a href=\"https://github.com/Electric-Blocks\">https://github.com/Electric-Blocks</a> for more info."

@app.route("/api", methods=["GET", "POST"])
def api():
    try:
        json.loads(request.data)
    except:
        raise JsonError("Could not parse json from request data")

    status = utils.get_or_error("status", request.json)
    if status == "SIM_REQUEST":
        return sim_request(request.json)
    elif status == "KEEP_ALIVE":
        return keep_alive()
    else:
        raise InvalidError(f"Status \"{status}\" is not a valid status code.")

# RESPONSES

def keep_alive():
    message = {}
    message["status"] = "KEEP_ALIVE"
    message["response"] = "Keep alive request acknowledged"
    return json.dumps(message)

def sim_request(data):
    is_three_phase = utils.get_or_error("3phase", data)
    is_estimate = utils.get_or_error("is_estimate", data)
    elements_dict = utils.get_or_error("elements", data)
    measurements_dict = utils.get_or_error("measurements", data)

    buses = {} # Used for matching bus UUIDs to index
    elements = {} # Used for matching ELEMENT UUIDs to index

    def process_potential_bus(key, value):
        """ Inner method for processing a positional argument that could be a BUS
            This function checks if the value is in the bus keys. This should never cause issues so long as UUID's aren't used for
            any other purpose except for bus identification and as long as there are no UUID collisions. Both of those cases seem
            exceptionally unlikely, so this should work fine.
        """
        if value in buses.keys():
            return buses[value]
        elif value == "None":
            return None
        else:
            return value   

    bus_list = [(uuid, element) for uuid, element in elements_dict.items() if utils.get_or_error("etype", element) == "bus"]
    element_list = [(uuid, element) for uuid, element in elements_dict.items() if utils.get_or_error("etype", element) != "bus" and utils.get_or_error("etype", element) != "switch"]
    switch_list = [(uuid, element) for uuid, element in elements_dict.items() if utils.get_or_error("etype", element) == "switch"]
    measurements_list = [(uuid, element) for uuid, element in measurements_dict.items() ] # ifutils.get_or_error("meas_type", element) == "measurements"
    
    net = pp.create_empty_network()

    #create_buses
    for uuid, bus in bus_list:
        element_type = "bus"
        req_props = utils.required_props[element_type]
        positional_args = [value for key, value in bus.items() if key in req_props ]
        optional_args = { key: value for key, value in bus.items() if (not key in req_props) and (not key == "etype")}
        index = pp.create_bus(net, *positional_args, **optional_args, name=uuid)
        buses[index] = uuid
    
    #create_elements
    for uuid, element in element_list:
        element_type = utils.get_or_error("etype", element)
        req_props = utils.required_props[element_type]
        positional_args = [process_potential_bus(key, value) for key, value in element.items() if key in req_props]
        optional_args = { key: value for key, value in element.items() if (not key in req_props) and (not key == "etype") } #and (not key == "in_service")
        
        #in_service_val = utils.get_or_error("in_service", element)
        index = None

        if element_type == "load":
            index = pp.create_load(net, *positional_args, **optional_args, name=uuid)

        elif element_type == "gen":            
            #min_q_mvar_val = utils.get_or_error("min_q_mvar", element) #min_q_mvar = min_q_mvar_val,
            index = pp.create_gen(net, *positional_args, **optional_args, name=uuid)

        elif element_type == "ext_grid":
            index = pp.create_ext_grid(net, *positional_args, **optional_args, name=uuid)

        # elif element_type == "line":
        #     pp.create_line(net, *positional_args, **optional_args, name=uuid)
        # elif element_type == "lineStd":
        #     pp.create_line(net, *positional_args, **optional_args, name=uuid)
        elif element_type == "line":
            index = pp.create_line_from_parameters(net, *positional_args, **optional_args, name=uuid)  

        # elif element_type == "trafo":
        #     pp.create_transformer(net, *positional_args, **optional_args, name=uuid)
        # elif element_type == "trafoStd":
        #     pp.create_transformer(net, *positional_args, **optional_args, name=uuid)
        elif element_type == "trafo":
            index = pp.create_transformer_from_parameters(net, *positional_args, **optional_args, name=uuid)

        elif element_type == "storage":
            index = pp.create_storage(net, *positional_args, **optional_args, name=uuid)

        elif element_type == "shunt":            
            index = pp.create_shunt(net, *positional_args, **optional_args, name=uuid)

        else:
            index = "INVALID"
            raise InvalidError(f"Element type {element_type} is invalid or not implemented!")
        
        elements[index] = uuid
        

    #create_switches
    for uuid, switch in switch_list:
        element_type = "switch"
        req_props = utils.required_props[element_type]
        positional_args = [process_potential_bus(key, value) for key, value in switch.items() if key in req_props]
        optional_args = { key: value for key, value in switch.items() if (not key in req_props) and (not key == "etype") }
        
        #in_service_val = bool(utils.get_or_error("in_service", element))
        
        et = positional_args[2]
        if et == "b":
            pass # This is handled by process_potential_buses
        if et == "l":
            positional_args[1] = pp.get_element_index(net, "line", positional_args[1])
        # elif et == "l":
        #     positional_args[1] = pp.get_element_index(net, "lineStd", positional_args[1])
        # elif et == "l":
        #     positional_args[1] = pp.get_element_index(net, "lineParam", positional_args[1])
        elif et == "t":
            positional_args[1] = pp.get_element_index(net, "trafo", positional_args[1])
        # elif et == "t":
        #     positional_args[1] = pp.get_element_index(net, "trafoStd", positional_args[1])
        # elif et == "t":
        #     positional_args[1] = pp.get_element_index(net, "trafoParam", positional_args[1])
        elif et == "t3":
            positional_args[1] = pp.get_element_index(net, "trafo3w", positional_args[1])
        elif et == "sh":
            positional_args[1] = pp.get_element_index(net, "shunt", positional_args[1])
        else:
            raise InvalidError(f"Invalid element type {et}. Must be b,l,t,t3,sh.")
        pp.create_switch(net, *positional_args, **optional_args, name=uuid)



    def process_potential_element(key, value):
        """ Inner method for processing a positional argument that could be a ELEMENT or a BUS
            This function checks if the value is in the ELEMENT/BUS keys. This should never cause issues so long as UUID's aren't used for
            any other purpose except for bus identification and as long as there are no UUID collisions. Both of those cases seem
            exceptionally unlikely, so this should work fine.
        """
        if value in buses.keys():
            return buses[value]
        elif value in elements.keys():
            return elements[value]
        elif value == "None":
            return None
        else:
            return value


    #for state_estimation - create measurements
    for uuid, measurement in measurements_list:
        prop_type = "measurement"
        req_props = utils.required_props[prop_type] 
        positional_args = [ process_potential_element(key, value) for key, value in measurement.items() if key in req_props ]        
        optional_args = { key: value for key, value in measurement.items() if (not key in req_props) and (not key == "meas_type")}
        
        msrmt_index = pp.create_measurement(net, *positional_args, name=uuid)
            #pp.create_measurement(net, meas_type="v", element_type="bus", value=1.006, std_dev=0.004, element=b1, side=None, check_existing=True, index=None, name="b1_v_pu")
    
    #run (runpp, runpp_3ph, estimate)
    try:
        if is_three_phase:
            pp.runpp_3ph(net)
        elif is_estimate: #go estimate run
            res_rn_max = est.remove_bad_data(net, init="flat", rn_max_threshold=3.0)
            res_est = est.estimate(net, init="flat")
            print("isRemovedBadData: ", res_rn_max)
            print("isEstimated: ", res_est)
            pp.runpp(net)            
        else:
            pp.runpp(net)                
    except LoadflowNotConverged:
        report = pp.diagnostic(net, report_style="compact", warnings_only=True)
        raise ConvError("Load flow did not converge.")
    except (KeyError, ValueError) as e:
        print("ERR: " + str(e))
        raise PPError(str(e))
    except Exception as e:
        print("Unknown exception has occured: " + str(e))
        raise PPError("Unknown exception has occured: " + str(e))

    print("RESULT RUNPP:")
    print(net.res_bus)
    print(net.res_line)
    print("RESULT RUNEST:")
    print(net.res_bus_est)
    print(net.res_line_est)

    message = {}
    message["status"] = "SIM_RESULT"
    results = {}

    for uuid,element in elements_dict.items():
        element_type = elements_dict[uuid]["etype"]
        if element_type == "switch": continue
        net["res_" + element_type] = net["res_" + element_type].fillna(0)
        results[uuid] = {}
        results[uuid]["etype"] = element_type
        index = pp.get_element_index(net, element_type, uuid, exact_match=True)
        results[uuid].update(net["res_" + element_type].iloc[index].to_dict())

    message["elements"] = results
    return json.dumps(message)

# PROGRAM MAIN ENTRY POINT


if __name__ == "__main__":
    """ Entry point for program
    Just calls run and starts listening for requests
    """
    load_dotenv()
    host_addr = os.getenv("EBPP_HOST", "0.0.0.0")
    host_port = os.getenv("EBPP_PORT", "1127")
    debug_flag = False
    argc = len(sys.argv)
    if argc == 1:
        print("No arguments passed. Using defaults.")
    elif argc == 2:
        if sys.argv[1] == "-d":
            print("Running flask in debug mode.")
            host_addr = "127.0.0.1"
            debug_flag = True
        else:
            print(f"The flag {sys.argv[1]} is not a valid flag.")
    else:
        print("Invalid number of arguments given.")
    app.run(host=host_addr, port=host_port, debug=debug_flag)
