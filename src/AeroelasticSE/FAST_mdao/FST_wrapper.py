import os
import sys
import subprocess

from FST_writer import FstInputWriter
from FST_reader import FstInputReader
from FST_vartrees import FstModel

class FstExternalCode(object):

    pass


class FstWrapper(FstExternalCode):

    FSTexe = ''   #Path to executable
    FSTInputFile = ''   #FAST input file (ext=.fst)
    fst_directory = ''   #Path to fst directory files

    def __init__(self):
        super(FstWrapper, self).__init__()

    def execute(self):


        print "Executing FAST"
        self.input_file = os.path.join(self.fst_directory, self.FSTInputFile)

        if (not os.path.exists(self.FSTexe)):
            sys.stderr.write("Can't find FAST executable: {:}\n".format(self.FSTexe))
            return 0
        
        print "Calling ", self.FSTexe
        print "Input file = ", self.input_file

        exec_str = []
        exec_str.append(self.FSTexe)
        exec_str.append(self.input_file)

        subprocess.call(exec_str)#, stdin=None, stdout=None, stderr=None, shell=False)
        

if __name__=="__main__":

    fst = FstWrapper()
    fst.FSTexe = 'C:/Models/FAST/FAST.exe'
#    fst.FSTexe = '/Users/pgraf/opt/windcode-7.31.13/build/FAST_glin64'  ## OC3 version
    #fst.FSTInputFile = 'C:/Models/FAST/ModelFiles/FASTmodel.fst'
    #fst.execute()

    # OC3 Example
    fst_input = FstInputReader()
    fst_writer = FstInputWriter()

    FAST_DIR = os.path.dirname(os.path.realpath(__file__))

    fst_input.fst_infile = 'NRELOffshrBsline5MW_Monopile_RF.fst'
    #fst_input.fst_directory = os.path.join(FAST_DIR,"OC3_Files")
    fst_input.fst_directory = "C:/Python27/NREL-Models/WISDEM/AeroelasticSE/src/AeroelasticSE/ModelFiles/OC3_Files"
    fst_input.ad_file_type = 1
    fst_input.fst_file_type = 1
    fst_input.execute() 

    fst_writer.fst_vt = fst_input.fst_vt
    fst_writer.fst_infile = 'FAST_Model.fst'
    fst_writer.fst_directory = os.path.join(FAST_DIR,"tmp")
    fst_writer.fst_vt.PtfmFile = "Platform.dat"
    fst_writer.fst_vt.TwrFile = "Tower.dat"
    fst_writer.fst_vt.BldFile1 = "Blade.dat"
    fst_writer.fst_vt.BldFile2 = fst_writer.fst_vt.BldFile1 
    fst_writer.fst_vt.BldFile3 = fst_writer.fst_vt.BldFile1 
    fst_writer.fst_vt.ADFile = "Aerodyn.ipt"
    fst_writer.execute()

    fst.FSTInputFile = fst_writer.fst_infile
    fst.fst_directory = fst_writer.fst_directory
    fst.execute()
