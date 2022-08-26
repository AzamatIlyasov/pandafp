import sys
import pandapower as pp
import os

#sys.path.append(r'C:\Program Files\DIgSILENT\PowerFactory 2021 SP3\Python\3.9')
# sys.path.append(r'C:\Program Files\DIgSILENT\PowerFactory 2022\Python\3.10')
# import powerfactory as pf
# app = pf.GetApplication()
# # from pandaplan.core.converter.powerfactory.pf2pp import from_pfd
# from pandapower.converter.powerfactory.export_pfd_to_pp import from_pfd
# net = from_pfd(app, prj_name="CSPA_Model", path_dst="G:\My Drive\___PROJECTS\pandafp\PandaPF_CSPA_Model.p")

net = pp.from_excel("net_PP_PF_CSPA_Model1.xlsx", convert=False)

print("NET:\n", net)

try:
    res_pp = pp.runpp(net, max_iteration=20, v_debug=True, enforce_q_lims=False, numba=False )
    #для учета Qmin Qmax - нужно включить enforce_q_lims=True 
    write_res_with_conv_false=True
    #pp.runpp(net, max_iteration=10,  numba=False) 
    print("isRunPP: ", res_pp)     
except Exception as e:    
    print("ОШИБКА_RUNPP: " + str(e))
    print("DIAGNOSTIC_RUNPP: ")
    report = pp.diagnostic(net, overload_scaling_factor=0.9 , report_style="compact", warnings_only=True)    
    report_full = pp.diagnostic(net)
    print("DIAGNOSTIC_RUNPP: report PRINT ")
    print(report)
    print("DIAGNOSTIC_RUNPP: report_full PRINT ")
    print(report_full)

pp.to_excel(net, "net_PP_PF_CSPA_Model1.xlsx")
print("------------------------------")
