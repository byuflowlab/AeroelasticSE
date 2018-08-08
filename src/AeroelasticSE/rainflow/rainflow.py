#function [Channels, ChanName, ChanUnit, FileID] = ReadFASTbinary(FileName)

import sys, os, numpy as np
import re

def mytostr(ascii_str):
    s = ''.join(chr(i) for i in ascii_str )                     
    return s

def error(s):
    raise ValueError, s

def ReadFASToutput(nb_FAST_output_file):

    file_rainflow = open(nb_FAST_output_file)
    line_rainflow = file_rainflow.readlines()

    # extract names fron non-binary FAST output file
    name_line = 6
    str_val = re.findall("\w+",line_rainflow[name_line])

    # extract data from non-binary FAST output file
    head_len = 8

    FAST_output_array = np.zeros([len(line_rainflow), len(str_val)])

    for k in range(head_len, len(line_rainflow)):
        int_val = re.findall("[-+]?\d+[\.]?\d*[eE]?[-+]?\d*", line_rainflow[k])
        for j in range(0, len(str_val)):
            FAST_output_array[k][j] = float(int_val[j])

    # return chan, name
    return FAST_output_array, str_val

# TODO: determine error in ReadFASTbinary function
def ReadFASTbinary(FileName):

    # Channels, ChannelNames = ReadFASTbinary(FileName)
    # Author: Bonnie Jonkman, National Renewable Energy Laboratory
    # (c) 2012, National Renewable Energy Laboratory
    # ported to python by Peter Graf (2014)
    #
    # Input:
    #  FileName      - string: contains file name to open
    #
    # Output:
    #  Channels      - 2-D array: dimension 1 is time, dimension 2 is channel 
    #  ChanName      - cell array containing names of output channels
    #                  output, indicating possible non-constant time step
    ###########################################################################
    LenName = 10  # number of characters per channel name
    LenUnit = 10 # number of characters per unit name

    if (os.path.isfile(FileName)):


        fid  = file( FileName, "rb" )
        #----------------------------        
        # get the header information
        #----------------------------

        FileID = np.fromfile(fid,dtype='int16', count=1)[0]
    
        NumOutChans  = np.fromfile (fid, count=1, dtype='int32')[0]             # The number of output channels, INT(4)
        NT           = np.fromfile( fid, count=1, dtype='int32')[0]             # The number of time steps, INT(4)


        if FileID == 1:
            TimeScl  = np.fromfile( fid, count=1, dtype='float64')           # The time slopes for scaling, REAL(8)
            TimeOff  = np.fromfile( fid, count=1, dtype='float64')           # The time offsets for scaling, REAL(8)
        else:
            TimeOut1 = np.fromfile( fid, count=1, dtype='float64')           # The first time in the time series, REAL(8)
            TimeIncr = np.fromfile( fid, count=1, dtype='float64')           # The time increment, REAL(8)

        ColScl       = np.fromfile( fid, count=NumOutChans, dtype='float32') # The channel slopes for scaling, REAL(4)
        ColOff       = np.fromfile( fid, count=NumOutChans, dtype='float32') # The channel offsets for scaling, REAL(4)

        LenDesc      = np.fromfile( fid, count=1,           dtype='int32' )  # The number of characters in the description string, INT(4)
        #DescStrASCII = np.fromfile( fid, count=LenDesc,     dtype='uint8' )  # DescStr converted to ASCII
        #DescStr      = mytostr(DescStrASCII )

        # print(NumOutChans)
        # quit()

        ChanName = []                   # initialize the ChanName cell array
        for iChan in range( 0,NumOutChans+1):


            ChanNameASCII = np.fromfile( fid, count=LenName, dtype='uint8' ) # ChanName converted to numeric ASCII
            ChanName.append( mytostr(ChanNameASCII))


        ChanUnit = []                   # initialize the ChanUnit cell array
        for iChan in range(0,NumOutChans+1):
            ChanUnitASCII = np.fromfile( fid, count=LenUnit, dtype='uint8' ) # ChanUnit converted to numeric ASCII
            ChanUnit.append(mytostr(ChanUnitASCII) )

        #-------------------------        
        # get the channel time series
        #-------------------------

        nPts        = NT*NumOutChans           # number of data points in the file   
        Channels    = np.zeros((NT,NumOutChans+1))  # output channels (including time in column 1)

        if FileID == 1:
            PackedTime = np.fromfile( fid, count=NT, dtype='int32' ) # read the time data
            if ( len(PackedTime) < NT ): 
               error('Could not read entire ' + FileName + ' file: read ' + str( len(PackedTime) ) + ' of ' + str( NT ) + ' time values.')
                 

        PackedData = np.fromfile( fid, count=nPts, dtype='int16' ) # read the channel data
        if ( len(PackedData) < nPts ): 
           error('Could not read entire ' + FileName + ' file: read ' + str( len(PackedData) ) + ' of ' + num2str( nPts ) + ' values.')
           
        fid.close()

        #-------------------------
        # Scale the packed binary to real data
        #-------------------------

    #     ip = 1
    #     for it = 1:NT
    #         for ic = 1:NumOutChans
    #             Channels(it,ic+1) = ( PackedData(ip) - ColOff(ic) ) / ColScl(ic) 
    #             ip = ip + 1
    #         end # ic       
    #     end %it
    #

        dat = np.reshape(PackedData,(NumOutChans,NT), order='F')
        dat = np.transpose(dat)
        for ic in range(0,NumOutChans):
            Channels[:,ic+1] = (dat[:,ic] - ColOff[ic] ) / ColScl[ic]
        
        if FileID == 1:
            Channels[:][0] = ( PackedTime - TimeOff ) / TimeScl
        else:
            Channels[:,0] = TimeOut1 + TimeIncr * np.array(range(0,NT))[:]
            
    else:
        error('Could not open the FAST binary file: ' + FileName)

    return Channels, ChanName

def write_txt(fname,names, chan):
    fout = file(fname,"w")
    for n in names:
        fout.write("%s " % n)
    fout.write("\n")
    nt = chan.shape[0]
    nc = chan.shape[1]
    for it in range(nt):
        for ic in range(nc):
            fout.write("%e " % chan[it,ic])
        fout.write("\n")
    fout.close()


def determine_peaks(data):
# Identify peaks and troughs in the time series.  The first and last
# points are considered peaks or troughs.  Sometimes the peaks can be flat
# for a while, so we have to deal with that nasty situation.

#
# Syntax is:  [peaks, nPeaks] = determine_peaks(timeSeriesData);
#
# where:
#        data           - array of time series data.                      
#        nPeaks         - number of identified peaks
#        peaks          - an array of the identified peaks

# Example:
#     [peaks, nPeaks] = determine_peaks(timeSeriesData);
#
# See also  mlife

    # This is a Matlab vector-optimized rountine.  Sorry if it is hard to understand.  GJH
    # It was verified against a much slower version (see MCrunch)   
    
    # ported to python by Peter Graf and verified against Gordie's matlab code

    dnotflat = np.array(data[(data[1:] - data[0:-1] !=0)])
    dend = np.array([data[-1]])
    data       = np.concatenate((dnotflat, dend))
    backdiff   = data[1:-1] - data[0:-2]
    forwdiff   = data[2:] - data[1:-1]
    signchange = np.sign(backdiff) + np.sign(forwdiff) 
    peakInds   = np.nonzero(signchange == 0)[0] + 1
    peaks      = np.concatenate((np.array([data[0]]), data[peakInds], np.array([data[-1]])))
    nPeaks     = len(peaks)

    return peaks, nPeaks

def rain_one(col, slope):
    # import the swig-ized rainflow.c code
    import _rainflow_swig as rf

    ## bare bones, operate on single column of data
    # constants
    UCMult = 0.5
    LUlt = 0
    LMF = 0
    equivFreq = 1.0
    PSF = 1.1
    nEquivalantCounts = 600/equivFreq

    peaks, nPeaks = determine_peaks(col)

    output = np.zeros(5*nPeaks,dtype="double")

    rf.rainflow(output, peaks, LMF, LUlt, UCMult)
            # output contains a 5 * nPeaks array of data:

    cycles = np.reshape(output, (nPeaks,5))        
    cycleRanges = cycles[:,0]
    cycleCounts = cycles[:,3]       
    #the "m" value corresponds to different Wholer exponents... "I" (Gordie) oiginally used 3 different exponents,
    # but we can just use 4 for the steel components (tower and mooring lines) and 10 for the fiberglass components (blades)
                    #here is the equation to calculate the damage equivalent load using the output of the rainflow function
    val = ( sum( cycleCounts *( cycleRanges **slope ) )/nEquivalantCounts )**( 1.0/slope )*PSF

    return val
    
def do_rainflow(files, output_array, SNslope, dir_saved_plots, Tmax=600, dT = 0.0125, rm_time=0.0, check_rm_time=False):
    ## orchestrates whole series of steps to read FAST output, then do rainflow counting to get loads

    # import the swig-ized rainflow.c code
    import _rainflow_swig as rf
    ## [prototype builds on Pgraf's mac with: 
    #swig -python rainflow_swig.i
    #gcc -c rainflow_swig.c rainflow_swig_wrap.c  -I/opt/local/Library/Frameworks/Python.framework/
    # Versions/2.7/include/python2.7/ -I/opt/local//Library/Frameworks/Python.framework/
    # Versions/2.7/lib/python2.7/site-packages/numpy/core/include/
    #gcc -shared rainflow_swig.o rainflow_swig_wrap.o -o _rainflow_swig.so /opt/local/Library/Frameworks/Python.framework/
    # Versions/2.7/lib/libpython2.7.dylib ]
    ##
    allres = []
    nslopes = SNslope.shape[0]

    for f in files:

        # === read output file === #

        # if last char in string is 'b', use ReadFASTbinary
        if f[-1] == 'b':
            chan, name = ReadFASTbinary(f)
        # if last char in string is 't', use ReadFASToutput
        elif f[-1] == 't':
            chan, name = ReadFASToutput(f)
        # else, throw error
        else:
            raise Exception('Unable to read FAST output file; check string name.')

        # === remove artificially noisy data === #
        orig_chan = chan
        temp_chan = chan[int(rm_time/dT):-1]

        # plot removed output data
        if check_rm_time:

            # show rm_time
            rm_time_show = 20.0

            time_chan = np.linspace(0,Tmax,len(chan[:,0]))
            time_temp_chan = np.linspace(Tmax-rm_time_show,Tmax,len(temp_chan[:,0]))
            import matplotlib.pyplot as plt
            plt.figure()
            plt.plot(time_chan,chan[:,5],label='original output')
            plt.plot(time_temp_chan, temp_chan[:,5],label='noise removed')
            plt.title('RootMxb1')
            plt.legend()
            plt.savefig(dir_saved_plots + '/noise_removed.eps')
            plt.show()

            quit()

        chan = temp_chan

        # constants
        UCMult = 0.5
        LUlt = 0
        LMF = 0
        equivFreq = 6.0
        PSF = 1.0
        #nEquivalantCounts = 600/equivFreq
        # nEquivalantCounts = Tmax/equivFreq
        nEquivalantCounts = (Tmax-rm_time)/equivFreq

        # peaks array
        peaks_list = []

        res = np.zeros((len(output_array),nslopes)) 
        for i in range(len(output_array)):

            p = output_array[i]

            peaks, nPeaks = determine_peaks(chan[:,p])
            output = np.zeros(5*nPeaks,dtype="double")

            peaks_list.append(peaks)

            rf.rainflow(output, peaks, LMF, LUlt, UCMult)

            # output contains a 5 * nPeaks array of data:
            cycles = np.reshape(output, (nPeaks,5))        
            cycleRanges = cycles[:,0]
            cycleCounts = cycles[:,3]

            check_peaks = False
            if check_peaks:
                if p == 5: # RootMxb1
                    print(peaks)
                    print(nPeaks)

                    print(cycleRanges)
                    print(cycleCounts)

                    print(nEquivalantCounts)

                    quit()

    #``the "m" value corresponds to different Wholer exponents... "I" (Gordie) oiginally used 3 different exponents,

            # but we can just use 4 for the steel components (tower and mooring lines) and 10 for the fiberglass components (blades)
            for m in range(nslopes): 
                #here is the equation to calculate the damage equivalent load using the output of the rainflow function
                val = ( sum( cycleCounts *( cycleRanges **SNslope[m,i] ) )/nEquivalantCounts )**( 1.0/SNslope[m,i] )*PSF
                res[i,m] = val

        allres.append(res)

    return allres, peaks_list, orig_chan, chan, name


if __name__=="__main__":

    files = ["Sims/DLCud_3601_Sea_24.0V0_04.5Hs_09.5Tp_00.0Wd_S001.outb"]

    # files = ['DLCud_3601_Sea_24.0V0_04.5Hs_09.5Tp_00.0Wd_S001.outb',
    #          'DLCud_3241_Sea_22.0V0_04.0Hs_09.0Tp_00.0Wd_S001.outb',
    #          'DLCud_2881_Sea_20.0V0_03.6Hs_08.5Tp_00.0Wd_S001.outb',
    #          'DLCud_2521_Sea_18.0V0_03.1Hs_08.0Tp_00.0Wd_S001.outb',
    #          'DLCud_2161_Sea_16.0V0_02.6Hs_07.6Tp_00.0Wd_S001.outb',
    #          'DLCud_1801_Sea_14.0V0_02.2Hs_07.5Tp_00.0Wd_S001.outb',
    #          'DLCud_1441_Sea_12.0V0_01.8Hs_07.4Tp_00.0Wd_S001.outb',
    #          'DLCud_1081_Sea_10.0V0_01.5Hs_07.7Tp_00.0Wd_S001.outb',
    #          'DLCud_0721_Sea_08.0V0_01.3Hs_08.0Tp_00.0Wd_S001.outb',
    #          'DLCud_0361_Sea_06.0V0_01.2Hs_08.3Tp_00.0Wd_S001.outb',
    #          'DLCud_0001_Sea_04.0V0_01.1Hs_08.5Tp_00.0Wd_S001.outb']
    #
    # files = [os.path.join("Sims", f) for f in files]

    ##get DELs for Blade edge:53 and flap:54 bending moment, tower SS:92 and FA:93, and
    ##anchor tension:100. Note: these might be different for different FAST

    ##output files
    ## these are literally the indices in the FAST output table of the fields of interest
    ## (in python they are 0-based)

    output_array = [3, 4, 5, 6, 7]
    ## these are the powers that the cycles are raised to in order to get the final fatigue.
    ## they are properties of the materials of the corresponding fields (so they are tied
    ## to the indices in "output_array"
    SNslope = np.array([[1,1,1,1,1],[ 8,  8, 3, 3, 3],
                        [10, 10, 4, 4, 4],
                        [12, 12, 5, 5, 5]], dtype="double")

    #SNslope = np.array([[1], [8], [10], [12]], dtype="double")

    allres = do_rainflow(files, output_array, SNslope)
    for i in range(len(files)):

        print(i)
        print allres[i]
