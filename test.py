import pandapower as pp
#create empty net
net = pp.create_empty_network()

#create buses
b1 = pp.create_bus(net, vn_kv=20., name="Bus 1")
b2 = pp.create_bus(net, vn_kv=0.4, name="Bus 2")
b3 = pp.create_bus(net, vn_kv=0.4, name="Bus 3")

#create bus elements
pp.create_ext_grid(net, bus=b1, vm_pu=1.02, name="Grid Connection")
pp.create_load(net, bus=b3, p_mw=0.1, q_mvar=0.05, name="Load")

#create branch elements
#tid = pp.create_transformer(net, hv_bus=b1, lv_bus=b2, std_type="0.4 MVA 20/0.4 kV", name="Trafo")
tid = pp.create_transformer_from_parameters(net, hv_bus=b1, lv_bus=b2, vn_hv_kv=20.0, vn_lv_kv=0.4, name="Trafo",
    sn_mva=0.40, vk_percent=6.0, vkr_percent=1.425, pfe_kw=1.35, i0_percent=0.3375)
    #shift_degree=150, tap_side="hv", vector_group="Dyn5", tap_neutral=0, tap_min=-2, tap_max=2, tap_step_percent=2.5, tap_step_degree=0, tap_phase_shifter=False)
#pp.create_line(net, from_bus=b2, to_bus=b3, length_km=0.1, name="Line",std_type="NAYY 4x50 SE")
test_args={'from_bus':b2, 'to_bus':b3, 'length_km':0.1}

pp.create_line_from_parameters(net, exec(**test_args), r_ohm_per_km=0.6420, 
    x_ohm_per_km=0.083, c_nf_per_km=210, max_i_ka=0.142) 
    #in_service=True, type="cs", q_mm2=50, alpha=0.00403)

print(net)

pp.runpp(net)
print(net.res_bus)
