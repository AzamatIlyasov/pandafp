import pandapower as pp
from pandapower import estimation as est
from pandapower.estimation import remove_bad_data
import numpy as np
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

#create empty net
net = pp.create_empty_network() 

#create buses
b1 = pp.create_bus(net, name="bus 1", vn_kv=1., index=1)
b2 = pp.create_bus(net, name="bus 2", vn_kv=1., index=2)
b3 = pp.create_bus(net, name="bus 3", vn_kv=1., index=3)

#create bus elements
pp.create_ext_grid(net, bus=b1,name="Grid Connection", index=10000)

#create static gen
pp.create_sgen(net, bus=b1,p_mw=1.1,q_mvar=0, sn_mva=None, name="Example static gen", index=None, scaling=1.0, type='wye', in_service=True, max_p_mw=None, min_p_mw=None, max_q_mvar=None, min_q_mvar=None, controllable=None, k=None, rx=None, current_source=True)

#load
pp.create_load


#create branch elements
l1 = pp.create_line_from_parameters(net, from_bus=b1, to_bus=b2, length_km=1., r_ohm_per_km=.01, x_ohm_per_km=.03, c_nf_per_km=0., max_i_ka=1, index=1)
l2 = pp.create_line_from_parameters(net, from_bus=b1, to_bus=b3, length_km=1., r_ohm_per_km=.02, x_ohm_per_km=.05, c_nf_per_km=0., max_i_ka=1, index=2)
l3 = pp.create_line_from_parameters(net, from_bus=b2, to_bus=b3, length_km=1., r_ohm_per_km=.03, x_ohm_per_km=.08, c_nf_per_km=0., max_i_ka=1, index=3)


sw_l1 = pp.create_switches(net, buses = [1,2], elements = [1,1], et=['l','l'], closed=True, type="CB", name="test_sw_l1", index=[1,2], z_ohm=0.01)
sw_l2 = pp.create_switches(net, buses = [1,3], elements = [2,2], et=['l','l'], closed=True, type="CB", name="test_sw_l2", index=[3,4], z_ohm=0.01)


print(net)

#create measure
 # V at bus 1 and 2 (in pu)
msrnt_index_vb = pp.create_measurement(net, meas_type="v", element_type="bus", value=-0.1, std_dev=-0.1, element=b1, side=None, check_existing=True, index=None, name="b1_v_pu")
pp.create_measurement(net, meas_type="v", element_type="bus", value=0.968, std_dev=0.004, element=b2, side=None, check_existing=True, index=None, name="b2_v_pu")

 # P and Q at bus2 (in MW, Mvar)
pp.create_measurement(net, meas_type="p", element_type="bus", value=0.501, std_dev=0.01, element=b2, name="b2_p_mwat")
pp.create_measurement(net, meas_type="q", element_type="bus", value=0.286, std_dev=0.01, element=b2, name="b2_q_mvar")

 # P and Q at line
msrnt_index_pl = pp.create_measurement(net, meas_type="p", element_type="line", value=0.888, std_dev=0.008, element=l1, side=b1, name="l1_b1_b2_p_mwat")
pp.create_measurement(net, meas_type="p", element_type="line", value=1.173, std_dev=0.008, element=l2, side=b1, name="l2_b1_b3_p_mwat")
pp.create_measurement(net, meas_type="q", element_type="line", value=0.568, std_dev=0.008, element=l1, side=b1, name="l1_b1_b2_q_mvar")
pp.create_measurement(net, meas_type="q", element_type="line", value=0.663, std_dev=0.008, element=l2, side=b1, name="l2_b1_b3_q_mvar")

pp.create_measurement(net, meas_type="p", element_type="line", value=1.0, std_dev=0.008, element=l1, side=b3, name="l1_b1_b2_p_mwat")

print("MEAS.BEF1:\n",net.measurement)


#go run
res_chi2 = est.chi2_analysis(net, init="flat")
print("isChi2: ", res_chi2)
res_rn_max = remove_bad_data(net, init="flat", rn_max_threshold=3.0)
print("isRemovedBadData: ", res_rn_max)

print("MEAS.AFTER:\n",net.measurement)

resEst = est.estimate(net, init="flat")

print("RESULT:")
print(" isEstimated: ", resEst)
print(net.res_bus_est)

#pp.runpp(net)
#print(net.res_bus)
pp.to_excel(net, "net_demo3_stest1.xlsx")

#plotting
# pltly.simple_plotly(net)
# pltly.vlevel_plotly(net)
# pltly.pf_res_plotly(net)

# plt.simple_plot(net)
# plt.simple_plot(net, plot_loads=True, plot_gens=True, plot_sgens=True, plot_line_switches=True)


