import os

from FST_reader import FstInputReader, FstInputBase
from FST_vartrees import FstModel

import copy

# Builder

class FstInputBuilder(object):
    """
    base class for setting up HAWC2 input data

    add additional design variables and methods in derived classes
    """

    fstIn = FstModel()
    fstS = FstModel()
    fstOut = FstModel()
    
    def __init__(self):
        
        super(FstInputBuilder,self).__init__()

    def initialize_inputs(self):

        self._logger.info('dublicating inputs')
        self.fstS = self.fstIn.copy()

    def execute(self):

        self._logger.info('updating inputs')
        # update outputs
        self.fstOut = self.fstS.copy()

class FUSEDWindInputBuilder(FstInputBuilder):
    """
    Component for translating FUSED-Wind input vartrees to HAWC2 inputs
    """

    # inputs = Instance(iotype='in')   #[AH] no Instance in omdao1
    
    def __init__(self):
        
        super(FUSEDWindInputBuilder,self).__init__()

    def execute(self):
        """
        check which vartrees are passed in the case 
        """

        # connect all variables
        if hasattr(self.inputs, 'environment') and hasattr(self.inputs, 'simulation'):

            self._logger.info('setting wind and simulation inputs')

            self.fstS.aero_vt.AirDens = self.inputs.environment.density
            self.fstS.aero_vt.KinVisc = self.inputs.environment.viscosity
            
            # Ignore TI, kappa, z0 (TODO: turbsim input file structure)
            self.fstS.simple_wind_vt.TimeSteps = 2

            self.fstS.simple_wind_vt.HorSpd = [self.inputs.environment.vhub] * 2
            self.fstS.simple_wind_vt.WindDir = [self.inputs.environment.direction] * 2
            self.fstS.simple_wind_vt.VerSpd = [0.0] * 2 # TODO: include?
            self.fstS.simple_wind_vt.HorShr = [0.0] * 2 # TODO: include?
            if self.inputs.environment.inflow_type == 'constant':
                self.fstS.simple_wind_vt.VerShr = [0.0] * 2
                self.fstS.simple_wind_vt.LnVShr = [0.0] * 2
            elif self.inputs.environment.inflow_type == 'log':
                self.fstS.simple_wind_vt.VerShr = [0.0] * 2
                self.fstS.simple_wind_vt.LnVShr = [0.0] * 2
            elif self.inputs.environment.inflow_type == 'powerlaw':
                self.fstS.simple_wind_vt.VerShr = [self.inputs.environment.shear_exp] * 2
                self.fstS.simple_wind_vt.LnVShr = [0.0] * 2
            elif self.inputs.environment.inflow_type == 'linear':
                self.fstS.simple_wind_vt.VerShr = [0.0] * 2
                self.fstS.simple_wind_vt.LnVShr = [0.0] * 2
            else:
                self.fstS.simple_wind_vt.VerShr = [0.0] * 2
                self.fstS.simple_wind_vt.LnVShr = [0.0] * 2             

            self.fstS.simple_wind_vt.GstSpd = [0.0] * 2 # TODO: include?

            self.fstS.simple_wind_vt.Time = [None] * 2            
            self.fstS.simple_wind_vt.Time[0] = self.inputs.simulation.time_start
            self.fstS.simple_wind_vt.Time[1] = self.inputs.simulation.time_stop
            self.fstS.aero_vt.DTAero = self.inputs.simulation.time_step

        # call parent that simply copies Ps to Pout
        super(FUSEDWindInputBuilder, self).execute()

'''class FUSEDWindOutputBuilderBase(Component):
    """
    Component for converting HAWC2 outputs to FUSED-Wind outputs
    """

    output = Slot(iotype='in', desc='HAWC2 output object')
    outputs = Slot(iotype='out', desc='FUSED-Wind output vartree')

    def execute(self):

        pass

class FUSEDWindIECOutputBuilder(FUSEDWindOutputBuilderBase):

    def execute(self):

        self._logger.info('Converting HAWC2 outputs to FUSED-Wind IEC outputs ..')'''

# Writer

class FstInputWriter(FstInputBase):

    def __init__(self):

        self.fst_vt = FstModel()

        self.fst_infile = ''   #Master FAST file
        self.fst_directory = ''   #Directory of master FAST file set
        self.fst_file_type = 0   #Enum(0, (0,1),iotype='in', desc='Fst file type, 0=old FAST, 1 = new FAST    
        self.ad_file_type = 0   #Enum(0, (0,1), iotype='in', desc='Aerodyn file type, 0=old Aerodyn, 1 = new Aerdyn
        
        self.case_id = 'DEFAULT'   #Case ID if writer is used as part of a case analyzer analysis

        self.fst_file = ''   #Case FAST file

    def InputConfig(self, **kwargs):
        for k, w in kwargs.iteritems():
            try:
                success = False
                if hasattr(self, k):
                    setattr(self,k,w)
                    success = True
                # [AH] Not sure if checking against all vartrees is a good idea
                # (problems if variables in different trees have same name)
                if hasattr(self.fst_vt, k):
                    setattr(self.fst_vt,k,w)
                    success = True
                if hasattr(self.fst_vt.simple_wind_vt, k):
                    setattr(self.fst_vt.simple_wind_vt,k,w)
                    success = True
                if hasattr(self.fst_vt.wnd_wind_vt, k):
                    setattr(self.fst_vt.wnd_wind_vt,k,w)
                    success = True
                if hasattr(self.fst_vt.platform_vt, k):
                    setattr(self.fst_vt.platform_vt,k,w)
                    success = True
                if hasattr(self.fst_vt.aero_vt, k):
                    setattr(self.fst_vt.aero_vt,k,w)
                    success = True
                if hasattr(self.fst_vt.fst_blade_vt, k):
                    setattr(self.fst_vt.fst_blade_vt,k,w)
                    success = True
                if hasattr(self.fst_vt.fst_tower_vt, k):
                    setattr(self.fst_vt.fst_tower_vt,k,w)
                    success = True
                # elif hasattr(self.fst_output_vt, k):
                #     setattr(self.fst_output_vt,k,w)
                # [AH] Not including outputs for now (has multiple sub-vartrees)
                if not success:
                    pass
                    # print "No object definition or variable tree has the attribute '{0}'.".format(k)
            except:
                pass
                # print "Error: Could assign attribute '{0}'".format(k)

    def execute(self):

        self.WindWriter()
        self.AeroWriter()        
        self.BladeWriter()
        self.TowerWriter()
        self.PlatformWriter()

        if self.case_id == 'DEFAULT':
            self.fst_file = os.path.join(self.fst_directory,self.fst_infile)
        else:
            case_file = self.case_id + '_' + self.fst_infile
            self.fst_file = os.path.join(self.fst_directory,case_file)
        ofh = open(self.fst_file, 'w')

        # FAST Inputs
        ofh.write('---\n')
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.description))
        ofh.write('---\n')
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.Echo))
        ofh.write('{:3}\n'.format(self.fst_vt.ADAMSPrep))
        ofh.write('{:3}\n'.format(self.fst_vt.AnalMode))
        ofh.write('{:3}\n'.format(self.fst_vt.NumBl))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TMax))
        ofh.write('{:.5f}\n'.format(self.fst_vt.DT ))
        ofh.write('---\n')
        ofh.write('{:3}\n'.format(self.fst_vt.YCMode))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TYCOn))
        ofh.write('{:3}\n'.format(self.fst_vt.PCMode))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TPCOn))
        ofh.write('{:3}\n'.format(self.fst_vt.VSContrl))
        ofh.write('{:.5f}\n'.format(self.fst_vt.VS_RtGnSp ))
        ofh.write('{:.5f}\n'.format(self.fst_vt.VS_RtTq ))
        ofh.write('{:.5f}\n'.format(self.fst_vt.VS_Rgn2K ))
        ofh.write('{:.5f}\n'.format(self.fst_vt.VS_SlPc ))
        ofh.write('{:3}\n'.format(self.fst_vt.GenModel))
        ofh.write('{:}\n'.format(self.fst_vt.GenTiStr))
        ofh.write('{:}\n'.format(self.fst_vt.GenTiStp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.SpdGenOn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TimGenOn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TimGenOf))
        ofh.write('{:3}\n'.format(self.fst_vt.HSSBrMode))
        ofh.write('{:.5f}\n'.format(self.fst_vt.THSSBrDp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TiDynBrk))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TTpBrDp1))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TTpBrDp2))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TTpBrDp3))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TBDepISp1))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TBDepISp2))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TBDepISp3))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TYawManS))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TYawManE))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NacYawF))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TPitManS1))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TPitManS2))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TPitManS3))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TPitManE1))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TPitManE2))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TPitManE3))
        ofh.write('{:.5f}\n'.format(self.fst_vt.BlPitch1 ))
        ofh.write('{:.5f}\n'.format(self.fst_vt.BlPitch2 ))
        ofh.write('{:.5f}\n'.format(self.fst_vt.BlPitch3 ))
        ofh.write('{:.5f}\n'.format(self.fst_vt.B1PitchF1))
        ofh.write('{:.5f}\n'.format(self.fst_vt.B1PitchF2))
        ofh.write('{:.5f}\n'.format(self.fst_vt.B1PitchF3))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.Gravity))
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.FlapDOF1))
        ofh.write('{:}\n'.format(self.fst_vt.FlapDOF2))
        ofh.write('{:}\n'.format(self.fst_vt.EdgeDOF))
        ofh.write('{:}\n'.format(self.fst_vt.TeetDOF))
        ofh.write('{:}\n'.format(self.fst_vt.DrTrDOF))
        ofh.write('{:}\n'.format(self.fst_vt.GenDOF))
        ofh.write('{:}\n'.format(self.fst_vt.YawDOF))
        ofh.write('{:}\n'.format(self.fst_vt.TwFADOF1))
        ofh.write('{:}\n'.format(self.fst_vt.TwFADOF2))
        ofh.write('{:}\n'.format(self.fst_vt.TwSSDOF1))
        ofh.write('{:}\n'.format(self.fst_vt.TwSSDOF2))
        ofh.write('{:}\n'.format(self.fst_vt.CompAero))
        ofh.write('{:}\n'.format(self.fst_vt.CompNoise))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.OoPDefl))
        ofh.write('{:.5f}\n'.format(self.fst_vt.IPDefl))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetDefl))
        ofh.write('{:.5f}\n'.format(self.fst_vt.Azimuth))
        ofh.write('{:.5f}\n'.format(self.fst_vt.RotSpeed))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NacYaw))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TTDspFA))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TTDspSS))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.TipRad))
        ofh.write('{:.5f}\n'.format(self.fst_vt.HubRad))
        ofh.write('{:3}\n'.format(self.fst_vt.PSpnElN))
        ofh.write('{:.5f}\n'.format(self.fst_vt.UndSling))
        ofh.write('{:.5f}\n'.format(self.fst_vt.HubCM))
        ofh.write('{:.5f}\n'.format(self.fst_vt.OverHang))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NacCMxn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NacCMyn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NacCMzn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TowerHt))
        ofh.write('{:.5f}\n'.format(self.fst_vt.Twr2Shft))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TwrRBHt))
        ofh.write('{:.5f}\n'.format(self.fst_vt.ShftTilt))
        ofh.write('{:.5f}\n'.format(self.fst_vt.Delta3))
        ofh.write('{:.5f}\n'.format(self.fst_vt.PreCone1))
        ofh.write('{:.5f}\n'.format(self.fst_vt.PreCone2))
        ofh.write('{:.5f}\n'.format(self.fst_vt.PreCone3))
        ofh.write('{:.5f}\n'.format(self.fst_vt.AzimB1Up))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.YawBrMass))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NacMass))
        ofh.write('{:.5f}\n'.format(self.fst_vt.HubMass))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TipMass1))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TipMass2))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TipMass3))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NacYIner))
        ofh.write('{:.5f}\n'.format(self.fst_vt.GenIner))
        ofh.write('{:.5f}\n'.format(self.fst_vt.HubIner))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.GBoxEff))
        ofh.write('{:.5f}\n'.format(self.fst_vt.GenEff))
        ofh.write('{:.5f}\n'.format(self.fst_vt.GBRatio))
        ofh.write('{:}\n'.format(self.fst_vt.GBRevers))
        ofh.write('{:.5f}\n'.format(self.fst_vt.HSSBrTqF))
        ofh.write('{:.5f}\n'.format(self.fst_vt.HSSBrDT))
        ofh.write('{:}\n'.format(self.fst_vt.DynBrkFi))
        ofh.write('{:.5f}\n'.format(self.fst_vt.DTTorSpr))
        ofh.write('{:.5f}\n'.format(self.fst_vt.DTTorDmp))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.SIG_SlPc))
        ofh.write('{:.5f}\n'.format(self.fst_vt.SIG_SySp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.SIG_RtTq))
        ofh.write('{:.5f}\n'.format(self.fst_vt.SIG_PORt))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.TEC_Freq))
        ofh.write('{:5}\n'.format(self.fst_vt.TEC_NPol))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TEC_SRes))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TEC_RRes))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TEC_VLL))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TEC_SLR))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TEC_RLR))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TEC_MR))
        ofh.write('---\n')
        ofh.write('{:3}\n'.format(self.fst_vt.PtfmModel))
        ofh.write('"{:}"\n'.format(self.fst_vt.PtfmFile))
        ofh.write('---\n')
        ofh.write('{:3}\n'.format(self.fst_vt.TwrNodes))
        ofh.write('"{:}"\n'.format(self.fst_vt.TwrFile))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.YawSpr))
        ofh.write('{:.5f}\n'.format(self.fst_vt.YawDamp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.YawNeut))
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.Furling))
        ofh.write('{:}\n'.format(self.fst_vt.FurlFile))
        ofh.write('---\n') 
        ofh.write('{:}\n'.format(self.fst_vt.TeetMod))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetDmpP))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetDmp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetCDmp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetSStP))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetHStP))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetSSSp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TeetHSSp))
        ofh.write('---\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.TBDrConN))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TBDrConD))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TpBrDT))
        ofh.write('---\n')
        ofh.write('"{:}"\n'.format(self.fst_vt.BldFile1))
        ofh.write('"{:}"\n'.format(self.fst_vt.BldFile2))
        ofh.write('"{:}"\n'.format(self.fst_vt.BldFile3))
        ofh.write('---\n') 
        ofh.write('"{:}"\n'.format(self.fst_vt.ADFile))
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.NoiseFile))
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.ADAMSFile))
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.LinFile))
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.SumPrint))
        ofh.write('{:}\n'.format(self.fst_vt.OutFileFmt))
        ofh.write('{:}\n'.format(self.fst_vt.TabDelim))
        ofh.write('{:}\n'.format(self.fst_vt.OutFmt))
        ofh.write('{:.5f}\n'.format(self.fst_vt.TStart))
        ofh.write('{:3}\n'.format(self.fst_vt.DecFact))
        ofh.write('{:.5f}\n'.format(self.fst_vt.SttsTime))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NcIMUxn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NcIMUyn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.NcIMUzn))
        ofh.write('{:.5f}\n'.format(self.fst_vt.ShftGagL))
        ofh.write('{:3}\n'.format(self.fst_vt.NTwGages))
        for i in range(self.fst_vt.NTwGages-1):
            ofh.write('{:3}, '.format(self.fst_vt.TwrGagNd[i]))
        ofh.write('{:3}\n'.format(self.fst_vt.TwrGagNd[-1]))
        ofh.write('{:3}\n'.format(self.fst_vt.NBlGages))
        for i in range(self.fst_vt.NBlGages-1):
            ofh.write('{:3}, '.format(self.fst_vt.BldGagNd[i]))
        ofh.write('{:3}\n'.format(self.fst_vt.BldGagNd[-1]))
    
        # Outlist
        ofh.write('Outlist\n')
        # Wind Motions
        out_list = []
        for i in self.fst_vt.fst_output_vt.wind_mot_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.wind_mot_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # Blade Motions
        out_list = []
        for i in self.fst_vt.fst_output_vt.blade_mot_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.blade_mot_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # Hub and Nacelle Motions
        out_list = []
        for i in self.fst_vt.fst_output_vt.hub_nacelle_mot_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.hub_nacelle_mot_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # Tower and Support Motions
        out_list = []
        for i in self.fst_vt.fst_output_vt.tower_support_mot_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.tower_support_mot_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # Wave Motions
        out_list = []
        for i in self.fst_vt.fst_output_vt.wave_mot_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.wave_mot_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # Blade Loads
        out_list = []
        for i in self.fst_vt.fst_output_vt.blade_loads_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.blade_loads_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # Hub and Nacelle Loads
        out_list = []
        for i in self.fst_vt.fst_output_vt.hub_nacelle_loads_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.hub_nacelle_loads_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # Tower and Support Loads
        out_list = []
        for i in self.fst_vt.fst_output_vt.tower_support_loads_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.tower_support_loads_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')
        # DOF
        out_list = []
        for i in self.fst_vt.fst_output_vt.dof_vt.__dict__.keys():
            if self.fst_vt.fst_output_vt.dof_vt.__dict__[i] == True:
                out_list.append(i)
        ofh.write('"')
        for i in range(len(out_list)):
            if out_list[i][0] != '_':
                ofh.write('{:}, '.format(out_list[i]))
        ofh.write('"\n')

        ofh.write('END\n')
        
        ofh.close()
    
    def PlatformWriter(self):
      
        platform_file = os.path.join(self.fst_directory,self.fst_vt.PtfmFile)
        ofh = open(platform_file, 'w')
        
        ofh.write('---\n')
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.description))
        # FEATURE FLAGS (CONT)
        ofh.write('Feature Flags\n')
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.PtfmSgDOF))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.PtfmSwDOF))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.PtfmHvDOF))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.PtfmRDOF))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.PtfmPDOF))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.PtfmYDOF))
        
        # INITIAL CONDITIONS (CONT)
        ofh.write('Initial conditions\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmSurge))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmSway))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmHeave))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmRoll))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmPitch))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmYaw))
        
        # TURBINE CONFIGURATION (CONT)
        ofh.write('Turbine Configuration\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.TwrDraft))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmCM))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmRef))
        
        # MASS AND INERTIA (CONT) 
        ofh.write('Mass and inertia\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmMass))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmRIner))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmPIner))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.PtfmYIner))
        
        # PLATFORM (CONT) 
        ofh.write('Platform\n')
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.PtfmLdMod))
        
        # TOWER (CONT) 
        ofh.write('Tower\n')
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.TwrLdMod))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.TwrDiam))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.TwrCA))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.TwrCD))
        
        # WAVES 
        ofh.write('Waves\n')
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WtrDens))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WtrDpth))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.WaveMod))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.WaveStMod))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WaveTMax))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WaveDT))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WaveHs))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WaveTp))
        if self.fst_vt.platform_vt.WavePkShp == 9999.9:
            ofh.write('DEFAULT\n')
        else:
            ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WavePkShp))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.WaveDir))
        ofh.write('{:5}\n'.format(self.fst_vt.platform_vt.WaveSeed1))
        ofh.write('{:5}\n'.format(self.fst_vt.platform_vt.WaveSeed2))
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.GHWvFile))
    
        # CURRENT
        ofh.write('Current\n')
        ofh.write('{:}\n'.format(self.fst_vt.platform_vt.CurrMod))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.CurrSSV0))

        if self.fst_vt.platform_vt.CurrSSDir == 9999.9:
            ofh.write('DEFAULT\n')
        else:
            ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.CurrSSDir))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.CurrNSRef))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.CurrNSV0))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.CurrNSDir))
        ofh.write('{:.5f}\n'.format( self.fst_vt.platform_vt.CurrDIV))
        ofh.write('{:.5f}\n'.format(self.fst_vt.platform_vt.CurrDIDir))
    
        # OUTPUT (CONT) 
        ofh.write('Output\n')
        ofh.write('{:5}\n'.format(self.fst_vt.platform_vt.NWaveKin))
        if self.fst_vt.platform_vt.NWaveKin != 0:
            ofh.write('{:5}\n'.format(self.fst_vt.platform_vt.WaveKinNd)) 
        else:
            ofh.write('\n')  
        
        ofh.close()
    
    def TowerWriter(self):

        tower_file = os.path.join(self.fst_directory,self.fst_vt.TwrFile)
        ofh = open(tower_file, 'w')

        ofh.write('---\n')
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.fst_tower_vt.description))
        ofh.write('Tower Parameters\n')
        ofh.write('{:3}\n'.format(self.fst_vt.fst_tower_vt.NTwInptSt))
        ofh.write('{:}\n'.format(self.fst_vt.fst_tower_vt.CalcTMode))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwrFADmp1))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwrFADmp2))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwrSSDmp1))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwrSSDmp2))
    
        # Tower Adjustment Factors
        ofh.write('Tower Adjustment Factors\n')
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.FAStTunr1))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.FAStTunr2))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.SSStTunr1))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.SSStTunr2))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.AdjTwMa))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.AdjFASt))
        ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.AdjSSSt))
     
        # Distributed Tower Properties   
        ofh.write('Distributed Tower Properties\n')
        ofh.write('---\n')
        ofh.write('---\n')
        hf = self.fst_vt.fst_tower_vt.HtFract
        md = self.fst_vt.fst_tower_vt.TMassDen
        fs = self.fst_vt.fst_tower_vt.TwFAStif
        ss = self.fst_vt.fst_tower_vt.TwSSStif
        gs = self.fst_vt.fst_tower_vt.TwGJStif
        es = self.fst_vt.fst_tower_vt.TwEAStif
        fi = self.fst_vt.fst_tower_vt. TwFAIner
        si = self.fst_vt.fst_tower_vt.TwSSIner
        fo = self.fst_vt.fst_tower_vt.TwFAcgOf
        so = self.fst_vt.fst_tower_vt.TwSScgOf
        for a1, a2, a3, a4, a5, a6, a7, a8, a9, a10 in zip(hf, md, fs, ss, gs, es, fi, si, fo, so):
            ofh.write('{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\n'.\
            format(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10))          
        
        # Tower Mode Shapes
        ofh.write('Tower Fore-Aft Mode Shapes\n')
        for i in range(5):
            ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwFAM1Sh[i]))
        for i in range(5):
            ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwFAM2Sh[i]))        
        ofh.write('Tower Side-to-Side Mode Shapes\n')         
        for i in range(5):
            ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwSSM1Sh[i]))
        for i in range(5):
            ofh.write('{:5}\n'.format(self.fst_vt.fst_tower_vt.TwSSM2Sh[i])) 
        
        ofh.close()
    
    def BladeWriter(self):
        
        blade_file = os.path.join(self.fst_directory,self.fst_vt.BldFile1)
        ofh = open(blade_file, 'w')
        
        ofh.write('---\n')
        ofh.write('---\n')
        ofh.write('{:}\n'.format(self.fst_vt.fst_blade_vt.description))
        ofh.write('---\n')
        ofh.write('{:4}\n'.format(self.fst_vt.fst_blade_vt.NBlInpSt))
        ofh.write('{:}\n'.format(self.fst_vt.fst_blade_vt.CalcBMode))
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.BldFlDmp1))
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.BldFlDmp2))
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.BldEdDmp1))
        ofh.write('---\n')
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.FlStTunr1))
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.FlStTunr2))
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.AdjBlMs))
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.AdjFlSt))
        ofh.write('{:.6f}\n'.format(self.fst_vt.fst_blade_vt.AdjEdSt))
        ofh.write('Blade properties\n')
        ofh.write('---\n')
        ofh.write('---\n')
        
        bf = self.fst_vt.fst_blade_vt.BlFract
        ac = self.fst_vt.fst_blade_vt.AeroCent
        st = self.fst_vt.fst_blade_vt.StrcTwst
        bm = self.fst_vt.fst_blade_vt.BMassDen
        fs = self.fst_vt.fst_blade_vt.FlpStff
        es = self.fst_vt.fst_blade_vt.EdgStff
        gs = self.fst_vt.fst_blade_vt.GJStff
        eas = self.fst_vt.fst_blade_vt.EAStff #[AH] was es (overwrote EdgStiff) -- changed to eas
        a = self.fst_vt.fst_blade_vt.Alpha
        fi = self.fst_vt.fst_blade_vt.FlpIner
        ei = self.fst_vt.fst_blade_vt.EdgIner 
        pr = self.fst_vt.fst_blade_vt.PrecrvRef
        ps = self.fst_vt.fst_blade_vt.PreswpRef
        fo = self.fst_vt.fst_blade_vt.FlpcgOf       
        eo = self.fst_vt.fst_blade_vt.Edgcgof
        feo = self.fst_vt.fst_blade_vt.FlpEAOf
        eeo = self.fst_vt.fst_blade_vt.EdgEAOf      

        for a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17  in \
            zip(bf, ac, st, bm, fs, es, gs, eas, a, fi, ei, pr, ps, fo, eo, feo, eeo):
            ofh.write('{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\n'.\
            format(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17))
 
        ofh.write('Blade Mode Shapes\n')
        for i in range(5):
            ofh.write('{:.4f}\n'.format(self.fst_vt.fst_blade_vt.BldFl1Sh[i]))
        for i in range(5):
            ofh.write('{:.4f}\n'.format(self.fst_vt.fst_blade_vt.BldFl2Sh[i]))           
        for i in range(5):
            ofh.write('{:.4f}\n'.format(self.fst_vt.fst_blade_vt.BldEdgSh[i]))      
         
        ofh.close() 
    
    def AeroWriter(self):

        if not os.path.isdir(os.path.join(self.fst_directory,'AeroData')):
            os.mkdir(os.path.join(self.fst_directory,'AeroData'))

        # create airfoil objects
        for i in range(self.fst_vt.aero_vt.blade_vt.NumFoil):
             af_name = os.path.join(self.fst_directory, 'AeroData', 'Airfoil' + str(i) + '.dat')
             self.fst_vt.aero_vt.blade_vt.FoilNm[i] = os.path.join('AeroData', 'Airfoil' + str(i) + '.dat')
             self.writeAirfoilFile(af_name, i, 2)

        ad_file = os.path.join(self.fst_directory,self.fst_vt.ADFile)
        ofh = open(ad_file,'w')
        
        ofh.write('Aerodyn input file for FAST\n')
        
        ofh.write('{:}\n'.format(self.fst_vt.aero_vt.SysUnits))
        ofh.write('{:}\n'.format(self.fst_vt.aero_vt.StallMod))        
        ofh.write('{:}\n'.format(self.fst_vt.aero_vt.UseCm))
        ofh.write('{:}\n'.format(self.fst_vt.aero_vt.InfModel))
        ofh.write('{:}\n'.format(self.fst_vt.aero_vt.IndModel))
        ofh.write('{:.3f}\n'.format(self.fst_vt.aero_vt.AToler))
        ofh.write('{:}\n'.format(self.fst_vt.aero_vt.TLModel))
        ofh.write('{:}\n'.format(self.fst_vt.aero_vt.HLModel))
        ofh.write('"{:}"\n'.format(self.fst_vt.aero_vt.WindFile))  
        ofh.write('{:.1f}\n'.format(self.fst_vt.aero_vt.HH))  
        ofh.write('{:.1f}\n'.format(self.fst_vt.aero_vt.TwrShad))  
        ofh.write('{:.1f}\n'.format(self.fst_vt.aero_vt.ShadHWid))  
        ofh.write('{:.1f}\n'.format(self.fst_vt.aero_vt.T_Shad_Refpt))  
        ofh.write('{:.3f}\n'.format(self.fst_vt.aero_vt.AirDens))  
        ofh.write('{:.9f}\n'.format(self.fst_vt.aero_vt.KinVisc))  
        ofh.write('{:2}\n'.format(self.fst_vt.aero_vt.DTAero))        

        ofh.write('{:2}\n'.format(self.fst_vt.aero_vt.blade_vt.NumFoil))
        for i in range (self.fst_vt.aero_vt.blade_vt.NumFoil):
            ofh.write('"{:}"\n'.format(self.fst_vt.aero_vt.blade_vt.FoilNm[i]))

        ofh.write('{:2}\n'.format(self.fst_vt.aero_vt.blade_vt.BldNodes))
        rnodes = self.fst_vt.aero_vt.blade_vt.RNodes
        twist = self.fst_vt.aero_vt.blade_vt.AeroTwst
        drnodes = self.fst_vt.aero_vt.blade_vt.DRNodes
        chord = self.fst_vt.aero_vt.blade_vt.Chord
        nfoil = self.fst_vt.aero_vt.blade_vt.NFoil
        prnelm = self.fst_vt.aero_vt.blade_vt.PrnElm
        ofh.write('Nodal properties\n')
        for r, t, dr, c, a, p in zip(rnodes, twist, drnodes, chord, nfoil, prnelm):
            ofh.write('{:.5f}\t{:.3f}\t{:.4f}\t{:.3f}\t{:5}\t{:}\n'.format(r, t, dr, c, a, p))

        ofh.close()

    def writeAirfoilFile(self, filename, a_i, mode=2):
        """
        Write the airfoil section data to a file using AeroDyn input file style.

        Arguments:
        filename - name (+ relative path) of where to write file

        Returns:
        nothing

        """

        f = open(filename, 'w')

        if (mode == 0):
            '''print >> f, 'AeroDyn airfoil file.  Compatible with AeroDyn v13.0.'
            print >> f, 'auto generated by airfoil.py'
            print >> f, 'airfoil.py is part of rotor TEAM'
            print >> f, '{0:<10d}\t{1:40}'.format(len(self.polars), 'Number of airfoil tables in this file')
            for p in self.polars:
                print >> f, '{0:<10g}\t{1:40}'.format(p.Re/1e6, 'Reynolds number in millions.')
                param = p.computeAerodynParameters(debug=debug)
                print >> f, '{0:<10f}\t{1:40}'.format(param[0], 'Control setting')
                print >> f, '{0:<10f}\t{1:40}'.format(param[1], 'Stall angle (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[2], 'Angle of attack for zero Cn for linear Cn curve (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[3], 'Cn slope for zero lift for linear Cn curve (1/rad)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[4], 'Cn at stall value for positive angle of attack for linear Cn curve')
                print >> f, '{0:<10f}\t{1:40}'.format(param[5], 'Cn at stall value for negative angle of attack for linear Cn curve')
                print >> f, '{0:<10f}\t{1:40}'.format(param[6], 'Angle of attack for minimum CD (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[7], 'Minimum CD value')
                for a, cl, cd in zip(p.alpha, p.cl, p.cd):
                    print >> f, '{0:<10f}\t{1:<10f}\t{2:<10f}'.format(a*R2D, cl, cd)
                print >> f, 'EOT'
                ## PG (1-19-13) added mode 2: coming from newer Aerodyn(?), but written for FAST 7 (?) ##'''
        elif (mode == 2):
            print >> f, 'AeroDyn airfoil file.'
            print >> f, 'auto generated by airfoil.py (part of rotor TEAM)'
            print >> f, '{0:<10d}\t{1:40}'.format(self.fst_vt.aero_vt.blade_vt.af_data[a_i].number_tables, 'Number of airfoil tables in this file')
            for i in range(self.fst_vt.aero_vt.blade_vt.af_data[a_i].number_tables):
                param = self.fst_vt.aero_vt.blade_vt.af_data[a_i].af_tables[i]
                print >> f, '{0:<10g}\t{1:40}'.format(i, 'Table ID parameter')
                print >> f, '{0:<10f}\t{1:40}'.format(param.StallAngle, 'Stall angle (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(0, 'No longer used, enter zero')
                print >> f, '{0:<10f}\t{1:40}'.format(0, 'No longer used, enter zero')
                print >> f, '{0:<10f}\t{1:40}'.format(0, 'No longer used, enter zero')
                print >> f, '{0:<10f}\t{1:40}'.format(param.ZeroCn, 'Angle of attack for zero Cn for linear Cn curve (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param.CnSlope, 'Cn slope for zero lift for linear Cn curve (1/rad)')
                print >> f, '{0:<10f}\t{1:40}'.format(param.CnPosStall, 'Cn at stall value for positive angle of attack for linear Cn curve')
                print >> f, '{0:<10f}\t{1:40}'.format(param.CnNegStall, 'Cn at stall value for negative angle of attack for linear Cn curve')
                print >> f, '{0:<10f}\t{1:40}'.format(param.alphaCdMin, 'Angle of attack for minimum CD (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param.CdMin, 'Minimum CD value')
                # for a, cl, cd, cm in zip(param.alpha, param.cl, param.cd, param.cm):
                #[AH] 'cm' removed here as well--double-check what this is all about
                for a, cl, cd in zip(param.alpha, param.cl, param.cd):
                    # print >> f, '{0:<10f}\t{1:<10f}\t{2:<10f}\t{3:<10f}'.format(a, cl, cd, cm)
                    print >> f, '{0:<10f}\t{1:<10f}\t{2:<10f}'.format(a, cl, cd)
        else:
            '''print >> f, 'AeroDyn airfoil file.'
            print >> f, 'auto generated by airfoil.py (part of rotor TEAM)'
            print >> f, '{0:<10d}\t{1:40}'.format(len(self.polars), 'Number of airfoil tables in this file')
            for i,p in enumerate(self.polars):
                param = p.computeAerodynParameters(mode=1,debug=debug)
                print >> f, '{0:<10g}\t{1:40}'.format(param[0], 'Table ID parameter')
                print >> f, '{0:<10f}\t{1:40}'.format(param[1], 'Stall angle (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[2], 'No longer used, enter zero')
                print >> f, '{0:<10f}\t{1:40}'.format(param[3], 'No longer used, enter zero')
                print >> f, '{0:<10f}\t{1:40}'.format(param[4], 'No longer used, enter zero')
                print >> f, '{0:<10f}\t{1:40}'.format(param[5], 'Angle of attack for zero Cn for linear Cn curve (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[6], 'Cn slope for zero lift for linear Cn curve (1/rad)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[7], 'Cn at stall value for positive angle of attack for linear Cn curve')
                print >> f, '{0:<10f}\t{1:40}'.format(param[8], 'Cn at stall value for negative angle of attack for linear Cn curve')
                print >> f, '{0:<10f}\t{1:40}'.format(param[9], 'Angle of attack for minimum CD (deg)')
                print >> f, '{0:<10f}\t{1:40}'.format(param[10], 'Minimum CD value') # is this 'Zero lift drag'?
                for a, cl, cd in zip(p.alpha, p.cl, p.cd):
                    print >> f, '{0:7.2f}\t{1:<7.3f}\t{2:<7.3}'.format(a*R2D, cl, cd)
                    #print >> f, '{0:<10f}\t{1:<10f}\t{2:<10f}'.format(a*R2D, cl, cd)'''
            
        f.close()

    # Wind Writer

    def WindWriter(self):
      
        if self.fst_vt.aero_vt.wind_file_type == 'hh':
    
            wind_file = os.path.join(self.fst_directory, self.fst_vt.aero_vt.WindFile)
            ofh = open(wind_file,'w')
        
            #ofh.write('{:}\n'.format(self.fst_vt.simple_wind_vt.description))
            #for i in range(6):
            #    ofh.write('! \n')
            for i in range(self.fst_vt.simple_wind_vt.TimeSteps):
                ofh.write('{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\n'.format(\
                          self.fst_vt.simple_wind_vt.Time[i], self.fst_vt.simple_wind_vt.HorSpd[i], self.fst_vt.simple_wind_vt.WindDir[i],\
                          self.fst_vt.simple_wind_vt.VerSpd[i], self.fst_vt.simple_wind_vt.HorShr[i],\
                          self.fst_vt.simple_wind_vt.VerShr[i], self.fst_vt.simple_wind_vt.LnVShr[i], self.fst_vt.simple_wind_vt.GstSpd[i]))
    
            ofh.close()

        elif self.fst_vt.aero_vt.wind_file_type == 'wnd':

            wind_file = os.path.join(self.fst_directory, self.fst_vt.aero_vt.WindFile)
            ofh = open(wind_file,'w')
        
            for i in range(self.fst_vt.wnd_wind_vt.TimeSteps):
                ofh.write('{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\t{:.5f}\n'.format(\
                          self.fst_vt.wnd_wind_vt.Time[i], self.fst_vt.wnd_wind_vt.HorSpd[i], self.fst_vt.wnd_wind_vt.WindDir[i],\
                          self.fst_vt.wnd_wind_vt.VerSpd[i], self.fst_vt.wnd_wind_vt.HorShr[i],\
                          self.fst_vt.wnd_wind_vt.VerShr[i], self.fst_vt.wnd_wind_vt.LnVShr[i], self.fst_vt.wnd_wind_vt.GstSpd[i]))
    
            ofh.close()
        
        else:
            print "TODO: Other wind file types bts and wnd"

'''def noise_example():

    # Noise example
    fst_input = FstInputReader()
    fst_writer = FstInputWriter()

    ad_file    = 'NREL5MW.ad'
    ad_file_type = 0
    blade_file = 'NREL5MW_Blade.dat'
    tower_file = 'NREL5MW_Monopile_Tower_RigFnd.dat'
    platform_file = 'NREL5MW_Monopile_Platform_RigFnd.dat'
    fst_file = 'NREL5MW_Monopile_Rigid.v7.02.fst'
    fst_file_type = 0
    FAST_DIR = os.path.dirname(os.path.realpath(__file__))
    fst_input.fst_infile_vt.template_path= os.path.join(FAST_DIR,"Noise_Files")
    ad_fname = os.path.join(fst_input.fst_infile_vt.template_path, ad_file)
    bl_fname = os.path.join(fst_input.fst_infile_vt.template_path, blade_file)
    tw_fname = os.path.join(fst_input.fst_infile_vt.template_path, tower_file)
    pl_fname = os.path.join(fst_input.fst_infile_vt.template_path, platform_file)
    fs_fname = os.path.join(fst_input.fst_infile_vt.template_path, fst_file)

    fst_input.fst_infile_vt.ad_file = ad_fname
    fst_input.fst_infile_vt.ad_file_type = ad_file_type
    fst_input.fst_infile_vt.blade_file = bl_fname
    fst_input.fst_infile_vt.tower_file = tw_fname
    fst_input.fst_infile_vt.platform_file = pl_fname
    fst_input.fst_infile_vt.fst_file = fs_fname
    fst_input.fst_infile_vt.fst_file_type = fst_file_type
    fst_input.execute() 

    fst_writer.fst_vt = fst_input.fst_vt
    fst_writer.execute()'''

def oc3_example():

    # OC3 Example
    fst_input = FstInputReader()
    fst_writer = FstInputWriter()

    FAST_DIR = os.path.dirname(os.path.realpath(__file__))

    fst_input.fst_infile = 'NRELOffshrBsline5MW_Monopile_RF.fst'
    fst_input.fst_directory = os.path.join(FAST_DIR,"OC3_Files")
    fst_input.ad_file_type = 1
    fst_input.fst_file_type = 1
    fst_input.execute() 

    fst_writer.fst_vt = fst_input.fst_vt
    fst_writer.fst_infle = 'FAST_Model.fst'
    fst_writer.fst_directory = os.path.join(FAST_DIR,"tmp")
    fst_writer.fst_vt.PtfmFile = "Platform.dat"
    fst_writer.fst_vt.TwrFile = "Tower.dat"
    fst_writer.fst_vt.BldFile1 = "Blade.dat"
    fst_writer.fst_vt.BldFile2 = fst_writer.fst_vt.BldFile1 
    fst_writer.fst_vt.BldFile3 = fst_writer.fst_vt.BldFile1 
    fst_writer.fst_vt.ADFile = "Aerodyn.ipt"
    fst_writer.execute()

if __name__=="__main__":

    #noise_example()
    
    oc3_example()
