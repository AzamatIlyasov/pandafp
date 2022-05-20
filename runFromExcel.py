import pandapower as pp
import pandas as pd
import pandapower.plotting.plotly as pltly
import pandapower.plotting as plt

net = pp.from_excel("net_cspa1.xlsx", convert=False)
try:
    pp.runpp(net, max_iteration=10,  numba=False)
except Exception as e:
        print("ОШИБКА: " + str(e))

pp.to_excel(net, "net_cspa_result1.xlsx")
print("RESULT:\n", net)

