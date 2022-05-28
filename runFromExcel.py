from sre_compile import isstring
import pandapower as pp
import pandas as pd
import pandapower.plotting.plotly as pltly
import pandapower.plotting as plt
import pandapower.estimation as est
import os
# import logging.config

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'simple': {
#             'format': '%(levelname)s: %(message)s'
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         '': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         },
#     },
# }
# logging.config.dictConfig(LOGGING)
# logging.getLogger(__name__).debug('This is a debug message')

#net = pp.from_excel(os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "EMS", "net_cspa2.xlsx"), convert=False)
net = pp.from_excel(os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "WACS", "wacs_new1.xlsx"), convert=False)

print("NET:\n", net)
print("MEAS.:\n", net.measurement)
meas = net.measurement

print("CHECK DATAS: val ")
for i, meas_val in enumerate(meas.value):
    res = meas_val 
    res /= 10
    #print(i, res)

print("CHECK DATAS:std_dev ")
for i, std_dev in enumerate(meas.std_dev):
    res = std_dev 
    res /= 10
    #print(i, res)
         
try:   
    res_chi2 = est.chi2_analysis(net, init="flat")
    print("isChi2: ", res_chi2)
    res_rn_max = est.remove_bad_data(net, init="flat", rn_max_threshold=3.0)
    print("isRemovedBadData: ", res_rn_max)
    res_est = est.estimate(net, init="flat")
    print("isEstimated: ", res_est) 
    res_pp = pp.runpp(net)  
    #pp.runpp(net, max_iteration=10,  numba=False) 
    print("isRunPP: ", res_pp) 

except Exception as e:
    print("ОШИБКА: " + str(e))

#pp.to_excel(net, os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "EMS","net_cspa_result2.xlsx"))
pp.to_excel(net, os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "WACS","wacs_new1_result.xlsx"))


# print("NET_BUS:\n", net.bus)
# print("NET_LOAD:\n", net.load)
# print("NET_GEN:\n", net.gen)
# print("NET_SHUNT:\n", net.shunt)
# print("NET_LINE:\n", net.line)
# print("NET_TRAFO:\n", net.trafo)

print("\nRESULT RUNPP:")
print(net.res_bus)
print(net.res_line)
print("\nRESULT RUNEST:")
print(net.res_bus_est)
print(net.res_line_est)
