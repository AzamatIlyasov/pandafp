import pandapower as pp
import pandapower.estimation as est


#create empty net
net = pp.create_empty_network() 

#create buses
b1 = pp.create_bus(net, name="bus 1", vn_kv=1., index=1)
b2 = pp.create_bus(net, name="bus 2", vn_kv=1., index=2)
b3 = pp.create_bus(net, name="bus 3", vn_kv=1., index=3)

#create bus elements
pp.create_ext_grid(net, bus=b1,name="Grid Connection")

#create branch elements
l1 = pp.create_line_from_parameters(net, 1, 2, 1, r_ohm_per_km=.01, x_ohm_per_km=.03, c_nf_per_km=0., max_i_ka=1)
l2 = pp.create_line_from_parameters(net, 1, 3, 1, r_ohm_per_km=.02, x_ohm_per_km=.05, c_nf_per_km=0., max_i_ka=1)
l3 = pp.create_line_from_parameters(net, 2, 3, 1, r_ohm_per_km=.03, x_ohm_per_km=.08, c_nf_per_km=0., max_i_ka=1)

net
#print(net)

#create measure
 # V at bus 1 and 2 (in pu)
pp.create_measurement(net, meas_type="v", element_type="bus", value=1.006, std_dev=0.004, element=b1, side=None, check_existing=True, index=None, name=None)
pp.create_measurement(net, meas_type="v", element_type="bus", value=0.968, std_dev=0.004, element=b2, side=None, check_existing=True, index=None, name=None)

 # P and Q at bus2 (in MW, Mvar)
pp.create_measurement(net, meas_type="p", element_type="bus", value=0.501, std_dev=0.01, element=b2)
pp.create_measurement(net, meas_type="q", element_type="bus", value=0.286, std_dev=0.01, element=b2)

 # P and Q at line
pp.create_measurement(net, meas_type="p", element_type="line", value=0.888, std_dev=0.008, element=l1, side=b1)
pp.create_measurement(net, meas_type="p", element_type="line", value=1.173, std_dev=0.008, element=l2, side=b1)
pp.create_measurement(net, meas_type="q", element_type="line", value=0.568, std_dev=0.008, element=l1, side=b1)
pp.create_measurement(net, meas_type="q", element_type="line", value=0.663, std_dev=0.008, element=l2, side=b1)

net.measurement

resultEst = est.estimate(net, init="flat")

print(resultEst)
print(net.res_bus_est)

#pp.runpp(net)
#print(net.res_bus)
