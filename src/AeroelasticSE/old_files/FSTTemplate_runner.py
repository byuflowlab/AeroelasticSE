""" This module implements FAST wrapper in terms of fusedwind's VariableTree based representation of a wind turbine.
The variable tree is a generic (wind-code agnostic) and hierarchical structural representation
of a modern wind turbine. 
This module is a very simple tutorial example of running FAST one time where the representation of
the turbine comes from this more structured representation (compared to the template-based approach).
"""

import os

from openmdao.lib.casehandlers.api import ListCaseRecorder

# from fusedwind.lib.caseiter import FUSEDCaseIterator
from fusedwind.runSuite.runCase import GenericRunCase
from fusedwind.runSuite.runBatch import FUSEDIECCaseIterator
from FusedFAST import openFAST 



if __name__=="__main__":
    # in real life these come from an input file:
    '''
    filedict = {'ts_exe' : "/Users/pgraf/opt/windcode-7.31.13/TurbSim/build/TurbSim_glin64",
    'ts_dir' : "/Users/pgraf/work/wese/fatigue12-13/from_gordie/SparFAST3.orig/TurbSim",
    'ts_file' : "TurbSim.inp",
    'fst_exe' : "/Users/pgraf/opt/windcode-7.31.13/build/FAST_glin64",
    'fst_dir' : "/Users/pgraf/work/wese/fatigue12-13/from_gordie/SparFAST3.orig",
    'fst_file' : "NRELOffshrBsline5MW_Floating_OC3Hywind.fst",
    'run_dir' : "run_dir"}
    '''
    filedict = {'ts_exe' : "/Users/pgraf/opt/windcode-7.31.13/TurbSim/build/TurbSim_glin64",
                'ts_dir' : "ModelFiles/OC3_FloatingOffshoreFiles/TurbSim",
                'ts_file' : "TurbSim.inp",
                'fst_exe' : "/Users/pgraf/opt/windcode-7.31.13/build/FAST_glin64",
                'fst_dir' : "ModelFiles/OC3_FloatingOffshoreFiles/",
                'fst_file' : "NRELOffshrBsline5MW_Floating_OC3Hywind.fst",
                'run_dir' : "run_dir"}
    
    '''
    filedict = {'ts_exe' : "C:/Models/TurbSim/TurbSim64.exe",
    'ts_dir' : "C:/Python27/NREL-Models/WISDEM/AeroelasticSE/src/AeroelasticSE/InputFilesToWrite",
    'ts_file' : "turbsim_template.inp",
    'fst_exe' : "C:/Models/FAST/FAST_v7.02.00d-bjj.exe",
    'fst_dir' : "C:/Python27/NREL-Models/WISDEM/AeroelasticSE/src/AeroelasticSE/FAST_VT/OC3_Files",
    'fst_file' : "NRELOffshrBsline5MW_Monopile_RF.fst",
    'run_dir' : "run_dir"} 
    '''
    
    iec = FUSEDIECCaseIterator()

    tmax = 5
    for w in [10, 12]:
        dlc = GenericRunCase("w%d" % w, ['Vhub','AnalTime'], [w,tmax])
        iec.cases.append(dlc)


    iec.setup_cases()
    wind_code = openFAST(filedict)
    iec.replace('runner', wind_code)

    iec.sequential = True

    print [c.name for c in iec.driver.workflow]
    print [c.name for c in iec.runner.driver.workflow]

    iec.run()
