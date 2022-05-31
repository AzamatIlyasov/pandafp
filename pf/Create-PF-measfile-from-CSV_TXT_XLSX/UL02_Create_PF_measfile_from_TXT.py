"""
Created May 2021
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
import pandas as pd
import numpy as np
import numpy.matlib
import os

# %% import text file
path = r'C:\Your Folder'
file = 'TXT_File.txt'

#path to save PowerFactory measfile (default = same as text file; add path below if you want to save measfile somewhere else)
path_output = path

#combine path and filename
strFile = os.path.join(path,file)

#import text file
dat_import=pd.read_csv(strFile, sep='\t', decimal=',', header=0)

# %% create PowerFactory measfile
#convert pandas to numpy array
datout = np.array(dat_import)

#convert to string
datout = datout.astype(str)

#add number of columns in header -> N-1 columns (time does not count as column)
datout = np.vstack ((np.empty((1,np.size(datout,1)), dtype="str"), datout))
datout[0,0] = str(np.size(datout,1)-1)

#filename of PowerFactory measfile
filename_out= file[0:-4] + '_PF_measfile_from_TXT.txt'

#save PowerFactory measfile as txt
filepath_out = os.path.join(path_output,filename_out)
np.savetxt(filepath_out, datout, fmt="%s")


