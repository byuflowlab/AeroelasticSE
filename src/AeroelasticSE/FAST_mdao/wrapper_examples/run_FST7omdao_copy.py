"""
Demonstration of setting up an OpenMDAO 1.x problem using the FST7Workflow component
(in FST7_aeroelasticsolver), which executes the FST7 reader, writer, and wrapper and assigns
all variables in the FAST outlist to OpenMDAO 'Unknowns'. It also
implements an "input config" function which allows the user to put all variables that they
wish to explicitly define into a dictionary. The input config function assigns these
variables to the correct locations in the variable tree.
"""
# Hacky way of doing relative imports
import os, sys
sys.path.insert(0, os.path.abspath(".."))
import numpy as np

from openmdao.api import Group, Problem, Component, IndepVarComp, ParallelGroup
from openmdao.api import SqliteRecorder
from FST7_aeroelasticsolver import FST7Workflow

# Initial OpenMDAO problem setup
top = Problem()
root = top.root = Group()

# Setup input config--file/directory locations, executable, types
caseid = "omdaoCase1.fst"
config = {}
config['fst_masterfile'] = 'Test01.fst'
config['fst_masterdir']= '/Users/bryceingersoll/Documents/GradPrograms/AeroelasticSE/src/AeroelasticSE/FAST_mdao/wrapper_examples/FST7inputfiles/'
config['fst_runfile'] = caseid
config['fst_rundir'] = '/Users/bryceingersoll/Documents/GradPrograms/AeroelasticSE/src/AeroelasticSE/FAST_mdao/wrapper_examples/rundir/'
config['fst_exe'] = '/Users/bryceingersoll/Documents/GradPrograms/FAST_glin32'
config['fst_file_type'] = 0
config['ad_file_type'] = 1

# Main AeroDyn File
# config['TowerHT'] = 90.0
config['NumBl'] = 3
config['Gravity'] = 9.80655
config['RotSpeed'] = 12.03
config['TipRad'] = 13.757
config['HubRad'] = 1.184

# TipRadius must be equal to HubRadius + SUM( DR(:) )
# Calculated in AeroSubs.f90

config['ShftTilt'] = -5.0

# Could not find attribute 'PreCone(1)'.
config['PreCone(1)'] = -2.5
config['PreCone(2)'] = -2.5
config['PreCone(3)'] = -2.5

config['TMax'] = 15 # Needs to be greater than 10 ?
config['DT'] = 0.005 # Needs to be less than 0.005

# # Blade File
config['NBlInpSt'] = 21
# Needs to match Blade Distributed Properties in AWT_Blades.dat
#
# # All of the columns below come from PreComp.  We are already computing them but they aren't exposed anywhere so this will require a little reworking to connect.  Will need to discuss with Ryan and/or me:
# # BlFract  AeroCent  StrcTwst  BMassDen  FlpStff     EdgStff     GJStff     EAStff      Alpha  FlpIner  EdgIner  PrecrvRef  PreswpRef  FlpcgOf  EdgcgOf   FlpEAOf  EdgEAOf
# These Defined in AWT_Blades.dat, DISTRIBUTED BLADE PROPERTIES

# Parameters to expose
# Could not find attribute 'BldEdDmp(1)'.
config['BldFlDmp(1)'] = 2.477465
config['BldFlDmp(2)'] = 2.477465
config['BldEdDmp(1)'] = 2.477465
# Could not find attribute 'FlStTunr(1)'.
config['FlStTunr(1)'] = 1.0
config['FlStTunr(2)'] = 1.0
config['AdjBlMs'] = 1.04536
config['AdjFlSt'] = 1.0
config['AdjEdSt'] = 1.0
#
# # AeroDyn File
config['IndModel'] = 'SWIRL'
config['TLModel'] = 'PRANDtl'
config['HLModel'] = 'PRANDtl'
# config['HH'] = 90.0
config['AirDens'] = 1.225
config['KinVisc'] = 1.464E-5
config['NumFoil'] = 10

#
# # These airfoil files use the exact same format so just need to pass names:
# # FoilNm      - Names of the airfoil files [NumFoil lines] (quoted strings)
# # 17        BldNodes    - Number of blade nodes used for analysis (-)
# # These should be exactly the same as in RotorAero (except DRNodes is not currently calculated, but that would be easy to do so):
# # RNodes   AeroTwst  DRNodes  Chord  NFoil  PrnElm
#
# # Parameters to expose
config['SysUnits'] = 'SI'
config['StallMod'] = 'BEDDOES'
config['UseCm'] = 'NO_CM'
config['InfModel'] = 'EQUIL'
config['AToler'] = 0.001
config['TwrShad'] = 0.0
config['ShadHWid'] = 9999.9
config['T_Shad_Refpt'] = 9999.9
config['DTAero'] = 0.02479
# config['DTAero'] = 0.004

# Add case to OpenMDAO problem
root.add('fast_component', FST7Workflow(config, caseid))

# Set up recorder
recorder = SqliteRecorder('omdaoCase1.sqlite')
top.driver.add_recorder(recorder)

# Perform setup and run OpenMDAO problem
top.setup()
top.run()

top.cleanup()   #Good practice, especially when using recorder

# Test to see how outputs change with different inputs
print(np.max(top['fast_component.RootMxc1']))
print(np.min(top['fast_component.RootMxc1']))