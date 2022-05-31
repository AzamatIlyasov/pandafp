# -*- coding: utf-8 -*-
"""
Created January 2021
@author: Michael Pertl, 
michael@thesmartinsights.com
www.thesmartinsights.com
------------------------------------------------------------------------------
DISCLAIMER: 
You may use the Code for any private or commercial purpose. However, you may not sell, 
sub-license, rent, lease, lend, assign or otherwise transfer, duplicate or otherwise 
reproduce, directly or indirectly, the Code in whole or in part. 

You acknowledge that the Code is provided “AS IS” and thesmartinsights.com expressly 
disclaims all warranties and conditions including, but not limited to, any implied 
warranties for suitability of the Code for a particular purpose, or any form of warranty 
that operation of the Code will be error-free.

You acknowledge that in no event shall thesmartinsights.com or any of its affiliates be 
liable for any damages arising out of the use of the Code or otherwise in connection with 
this agreement, including, without limitation, any direct, indirect special, incidental 
or consequential damages, whether any claim for such recovery is based on theories of 
contract, negligence, and even if thesmartinsights.com has knowledge of the possibility 
of potential loss or damage.
------------------------------------------------------------------------------- 
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys
sys.path.append(r'C:\Program Files\DIgSILENT\PowerFactory 2021 SP1\Python\3.8')
if __name__ == "__main__":
    import powerfactory as pf
app = pf.GetApplication()
if app is None:
    raise Exception('getting Powerfactory application failed')
#------------------------------------------------------------------------------

def getResults():    
    #get result file
    elmRes = app.GetFromStudyCase('*.ElmRes')    
    app.ResLoadData(elmRes)
  
    #Get number of rows and columns
    NrRow = app.ResGetValueCount(elmRes,0)
    
    #get objects of interest
    oSG1 = app.GetCalcRelevantObjects('G1.ElmSym')[0]
    oBus1 = app.GetCalcRelevantObjects('Bus 1.ElmTerm')[0]
    oLine4_5 = app.GetCalcRelevantObjects('Line 4-5.ElmLne')[0]

    #Get index of variable of interest
    ColIndex_time = app.ResGetIndex(elmRes,elmRes,'b:tnow')
    ColIndex_ut = app.ResGetIndex(elmRes,oSG1,'s:ut')
    ColIndex_P = app.ResGetIndex(elmRes,oSG1,'s:P1')
    ColIndex_Q = app.ResGetIndex(elmRes,oSG1,'s:Q1')
    ColIndex_speed = app.ResGetIndex(elmRes,oSG1,'s:xspeed')
    ColIndex_u_bus1 = app.ResGetIndex(elmRes,oBus1,'m:u')
    ColIndex_loading_line_4_5 = app.ResGetIndex(elmRes,oLine4_5,'c:loading')
    
    #pre-allocate result variables
    result_time = np.zeros((NrRow,))
    result_ut = np.zeros((NrRow))
    result_P = np.zeros((NrRow))
    result_Q = np.zeros((NrRow))    
    result_speed = np.zeros((NrRow))    
    result_u_bus1 = np.zeros((NrRow))    
    result_loading_line_4_5 = np.zeros((NrRow))    
    
    #get results for each time step
    for i in range(NrRow):    
        result_time[i] = app.ResGetData(elmRes,i,ColIndex_time)[1]
        result_ut[i] = app.ResGetData(elmRes,i,ColIndex_ut)[1]
        result_P[i] = app.ResGetData(elmRes,i,ColIndex_P)[1]
        result_Q[i] = app.ResGetData(elmRes,i,ColIndex_Q)[1]       
        result_speed[i] = app.ResGetData(elmRes,i,ColIndex_speed)[1]       
        result_u_bus1[i] = app.ResGetData(elmRes,i,ColIndex_u_bus1)[1]       
        result_loading_line_4_5[i] = app.ResGetData(elmRes,i,ColIndex_loading_line_4_5)[1]       
    
    results = pd.DataFrame()
    results['time'] = result_time
    results['P'] = result_P
    results['Q'] = result_Q
    results['ut'] = result_ut
    results['speed'] = result_speed
    results['u_bus1'] = result_u_bus1
    results['loading_line_4_5'] = result_loading_line_4_5
                
    return results
#%% load flow
#define project name and study case    
projName =   '_TSI_nine_bus_system'
study_case = '01_Study_Case.IntCase'

#activate project
project = app.ActivateProject(projName)
proj = app.GetActiveProject()

#get the study case folder and activate project
oFolder_studycase = app.GetProjectFolder('study')
oCase = oFolder_studycase.GetContents(study_case)[0]
oCase.Activate()

#get load flow object and execute
oLoadflow = app.GetFromStudyCase('ComLdf') #get load flow object
oLoadflow.Execute() #execute load flow

#get the generators and their active/reactive power and loading
Generators = app.GetCalcRelevantObjects('*.ElmSym')
for gen in Generators: #loop through list
    name = getattr(gen, 'loc_name') # get name of the generator
    actPower = getattr(gen,'c:p') #get active power
    reacPower = getattr(gen,'c:q') #get reactive power
    genloading = getattr(gen,'c:loading') #get loading
    #print results
    print('%s: P = %.2f MW, Q = %.2f MVAr, loading = %.0f percent' %(name,actPower,reacPower,genloading))

print('-----------------------------------------')

#get the lines and print their loading
Lines=app.GetCalcRelevantObjects('*.ElmLne')
for line in Lines: #loop through list
    name = getattr(line, 'loc_name') # get name of the line
    value = getattr(line, 'c:loading') #get value for the loading
    #print results
    print('Loading of the line: %s = %.2f percent' %(name,value))

print('-----------------------------------------')

#get the buses and print their voltage
Buses=app.GetCalcRelevantObjects('*.ElmTerm')
for bus in Buses: #loop through list
    name = getattr(bus, 'loc_name') # get name of the bus
    amp = getattr(bus, 'm:u1') #get voltage magnitude
    phase = getattr(bus, 'm:phiu') #get voltage angle
    #print results
    print('Voltage at %s = %.2f pu %.2f deg' %(name,amp,phase))

#%% RMS simulation and retrieving of results

#define project name and study case    
projName = '_TSI_nine_bus_system'
study_case = '01_Study_Case.IntCase'

#activate project
project = app.ActivateProject(projName)
proj = app.GetActiveProject()

#get the study case folder and activate project
oFolder_studycase = app.GetProjectFolder('study')
oCase = oFolder_studycase.GetContents(study_case)[0]
oCase.Activate()

# calculate initial conditions
oInit = app.GetFromStudyCase('ComInc') #get initial condition calculation object
oInit.Execute()

#run RMS-simulation
oRms = app.GetFromStudyCase('ComSim') #get RMS-simulation object
oRms.Execute()

#retrieve results
RES = getResults()

#%% plot

left = 0.01  # the left side of the subplots of the figure
right = 0.99   # the right side of the subplots of the figure
bottom = 0.01  # the bottom of the subplots of the figure
top = 0.99     # the top of the subplots of the figure
wspace = 0.4  # the amount of width reserved for space between subplots,
              # expressed as a fraction of the average axis width
hspace = 0.3  # the amount of height reserved for space between subplots,
              # expressed as a fraction of the average axis height

plt.figure()
plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)
plt.subplot(4,1,1)
plt.plot(RES['time'],RES['P'], color='black',label = 'G1')
plt.grid(True)
ax = plt.gca()
ax.axes.xaxis.set_ticklabels([])
plt.xlim(0,20)
# plt.ylim(0.99,1.04)
plt.locator_params(axis='y', nbins =5)
plt.ylabel('active \npower (MW)')
plt.legend()

plt.subplot(4,1,2)
plt.plot(RES['time'],RES['Q'], color='blue',label = 'G1')
plt.grid(True)
ax = plt.gca()
ax.axes.xaxis.set_ticklabels([])
plt.xlim(0,20)
plt.locator_params(axis='y', nbins =5)
plt.ylabel('reactive \npower (MVAr)')
plt.legend()

plt.subplot(4,1,3)
plt.plot(RES['time'],RES['u_bus1'], color='red',label = 'Bus 1')
plt.grid(True)
ax = plt.gca()
ax.axes.xaxis.set_ticklabels([])
plt.xlim(0,20)
plt.locator_params(axis='y', nbins =5)
plt.ylabel('voltage (pu)')
plt.legend()


plt.subplot(4,1,4)
plt.plot(RES['time'],RES['loading_line_4_5'], color='green',label = 'line 4-5')
plt.grid(True)
plt.xlim(0,20)
plt.locator_params(axis='y', nbins =5)
plt.xlabel('time (s)')
plt.ylabel('loading (%)')
plt.legend()


