import WACS_scheme as WACS
import pandapower as pp
import pandas as pd
import pandapower.plotting.plotly as pltly
import pandapower.plotting as plt

net = WACS.WACS_scheme()

pp.runpp(net)
print(net.res_line)
#pp.to_excel(net, "pandawacs1", include_results=True)

#plotting
pltly.simple_plotly(net)
pltly.vlevel_plotly(net)
pltly.pf_res_plotly(net)

plt.simple_plot(net, plot_loads=True, plot_gens=True, plot_sgens=True, plot_line_switches=True)
