# runTurbSim.py
# 2013 12 17

# TurbSim model - called by ???
# Runs TurbSim
#   - does not use OpenMDAO

"""
This module is a simple wrapper for `TurbSim <https://wind.nrel.gov/designcodes/preprocessors/turbsim/>`_

"""

import sys, os
import numpy as np
import subprocess
import platform
import random


class runTurbSim(object):
    """ A class for running TurbSim """

    ## these need to be supplied:
    ts_exe = None
    ts_file = None
    ts_dir = None
    run_dir = None

    tsDict = {}

    def write_inputs(self):
        """ read TurbSim templates, then write TurbSim inputs """
        if (self.run_dir == self.ts_dir):
            raise ValueError, "run_dir == fst_dir, you cannot run directly in the template directory"
        if (not os.path.isdir(self.run_dir)):
            os.mkdir(self.run_dir)

        self.readTemplate()
        self.writeInput()

    def readTemplate(self):
        """ read **TurbSim** input file and save lines """

        fname = os.path.join(self.ts_dir, self.ts_file)
        print "trying to open ", fname
        try:
            self.lines_inp = file(fname).readlines()
        except:
            sys.stdout.write ("Error opening %s" % fname)
            return 0

    def writeInput(self):
        """ write the input file, using self.tsDict to override values in template inputs.
        """
        self.run_name = self.ts_file.split(".")[0]
        try:
            fname = os.path.join(self.run_dir, self.ts_file)    
            ofh = open(fname,'w')
        except:
            sys.stdout.write ("Error opening %s\n" % fname)
            return 0

        for line in self.lines_inp:
            if (line.startswith('---')):
                ofh.write(line)
                continue

            flds = line.strip().split()

            """ If the second field in the line is present in the dictionary,
                  write the new value
                Otherwise
                  write the original line """

            if (len(flds) > 1 and flds[1] in self.tsDict):
                val = self.tsDict[flds[1]]
                # hack to prevent wind so low that TurbSim crashes
                if (flds[1] == "URef"):
                    val = max(0.01, val)
                f0 = '{:.12f}    '.format(val)
                if (flds[1] == "RandSeed1"):
                    f0 = '%d' % val                    
                oline = ' '.join([f0] + flds[1:])
#                oline = "%.12f    %s" % (val, flds[1])
                ofh.write(oline)
                ofh.write('\n')
            else:
                ofh.write(line)

        ofh.close()
        return 1

    # the real execute (no args)
    def execute(self):
        """ use subprocess to run **TurbSim**.
        Returns

        - ret (integer)
            return code from subprocess.call()
        """
        
        if 'RandSeed1' not in self.tsDict:
            self.tsDict['RandSeed1'] = random.randrange(-2147483648,2147483648)
        self.write_inputs()  ## assumes self.tsDict already set        
        input_name = os.path.join(self.run_dir, self.ts_file)    

        exe_name = self.ts_exe
        if (not os.path.exists(exe_name)):
            sys.stderr.write("Can't find TurbSim executable: {:}\n".format(exe_name))
            return 0
        curdir = os.getcwd()
        os.chdir (self.run_dir)  ###note, change to run_dir
        print "calling TurbSim:", exe_name
        print "input file=", input_name
#        tsstdout = file("TurbSim.stdout", "w")
#        ret = subprocess.call([exe_name, input_name], stdout=tsstdout )
        ret = subprocess.call([exe_name, input_name])
#        tsstdout.close()
        os.chdir(curdir) ## restore dir
        return ret

    def set_dict(self, ts_dict):
        self.tsDict = ts_dict

if __name__=="__main__":
    """ simple example usage """
    from AeroelasticSE.runTurbSim import runTurbSim

    ts = runTurbSim()
    ts.ts_exe = "/Users/pgraf/opt/windcode-7.31.13/TurbSim/build/TurbSim_glin64"

    #abs path
    ts.ts_dir = "/Users/pgraf/work/wese/fatigue12-13/from_gordie/SparFAST3.orig/TurbSim"
    ts.ts_file = "TurbSim.inp"

    #relative path
#    ts.ts_dir = "TurbSimTest"
#    ts.ts_file = "turbsim_template.inp"

    ts.run_dir = "turbsim_test_run"

    ws = 12.34
    tmax = 2
    ts.set_dict({"URef": ws, "AnalysisTime":tmax, "UsableTime":tmax})
    ts.execute()

