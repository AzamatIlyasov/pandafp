import pandapower as pp

#create empty net
net = pp.create_empty_network()
trf = pp.available_std_types(net, element='trafo')
line = pp.available_std_types(net, element='line')

print(net)
print(trf)
print(line)

