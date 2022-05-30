from sre_compile import isstring
import pandapower as pp
import pandas as pd
import pandapower.plotting.plotly as pltly
import pandapower.plotting as plt
import pandapower.estimation as est
import os

import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
logging.config.dictConfig(LOGGING)
logging.getLogger(__name__).debug('This is a debug message')

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

# try:
#     res_pp = pp.runpp(net, max_iteration=10, v_debug=True, enforce_q_lims=False )
#     #для учета Qmin Qmax - нужно включить enforce_q_lims=True 
#     write_res_with_conv_false=True
#     #pp.runpp(net, max_iteration=10,  numba=False) 
#     print("isRunPP: ", res_pp) 

#     #pp.to_excel(net, os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "WACS","wacs_new1_result10.xlsx"))
# except Exception as e:
#     pp.to_excel(net, os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "EMS","net_cspa2_result.xlsx"))
#     #pp.to_excel(net, os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "WACS","wacs_new1_result10.xlsx"))
#     print("ОШИБКА_RUNPP: " + str(e))
#     #report = pp.diagnostic(net, overload_scaling_factor=0.9 )#, report_style="compact")#, warnings_only=True)
#     #report_full = pp.diagnostic(net)
#     #print(report)

print("-------------")
     #pp.create_measurement
try:   
    #init - flat slack results
    #algorithm - wls  irwls  wls_with_zero_constraint  opt  lp
    #estimator - wls  lav  ql  qc  shgm  shgm  lav
    # res_chi2 = est.chi2_analysis(net, init="slack", maximum_iterations = 20)
    # print("isChi2: ", res_chi2)
    res_rn_max = est.remove_bad_data(net, init="slack", rn_max_threshold=3.0, maximum_iterations = 30, tolerance=0.01)
    print("isRemovedBadData: ", res_rn_max)
    res_est = est.estimate(net, init="slack", maximum_iterations = 30, tolerance=0.01)
    print("isEstimated: ", res_est) 
except Exception as e:
    print("ОШИБКА_EST: " + str(e))
    

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

#plotting
#pltly.pf_res_plotly(net, figsize = 2, bus_size=20, line_width=1.5, filename="cspa-respf-plot.html")

#pltly.simple_plotly(net, figsize = 2, bus_size=10, line_width=1, filename="wacs-simple-plot.html")
#pltly.vlevel_plotly(net, figsize = 2, bus_size=20, line_width=1.5, filename="wacs-vlevel-plot.html")
#pltly.pf_res_plotly(net, figsize = 2, bus_size=20, line_width=1.5, filename="wacs-respf-plot.html")

#pp.to_excel(net, os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "EMS","net_cspa2_result.xlsx"))
pp.to_excel(net, os.path.join("C:", "\FILES", "PROJECTS", "pandafp", "demo", "WACS","wacs_new1_result_est1.xlsx"))