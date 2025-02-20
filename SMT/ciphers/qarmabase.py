'''
Created on Feb 21, 2024

@author: XXXXXX
@author: XXXXXX
'''

from ciphers.cipher import AbstractCipher

from parser import stpcommands
from tabulate import tabulate

verbose = True

class QarmaBase(AbstractCipher):
    """
    Common methods for QARMAv1, QARMAv2
    """
    name = ""

    def getFormatString(self):
        pass

    def declareVariables(self, parameter, name, stp_file):
        var = []
        for i in range(parameter):
            temp = ["{}{}r{}".format(name, j, i) for j in range(16)]
            stpcommands.setupVariables(stp_file, temp, self.wordsize)
            var.append(temp)
        return var

    def declareSingleBitVariables(self, parameter, name, stp_file):
        var = []
        for i in range(parameter):
            temp = ["{}{}r{}".format(name, j, i) for j in range(16)]
            stpcommands.setupVariables(stp_file, temp, 1)
            var.append(temp)
        return var

    # The next method will set up for the S-Box, State and Twear Permutation,
    # and Matrix rotations for each cipher of the family.
    # It must be overridden.
    def setupComponents(self, stp_filename, parameters):
        # MIDORI sb0 S0box
        self.sbox = []
        # State Permutation
        self.TAU      = []
        self.TAU_INV  = []
        # Tweak permutation
        self.TWEAK_P     = []
        self.TWEAK_P_INV = []
        # MC ROTATIONS
        self.ROT = [0, 0, 0]

    # The next method will set up the tweak schedule.
    # It must be overridden.
    def tweakSchedule(self, parameters, stp_file):
        pass

    # The next method will create the STP program for the cipher.
    # In most cases for a 64-bit QARMA family member it will not need to be overridden.
    # WARNING, this assumes wordsize = 4
    def createSTP(self, stp_filename, parameters):
        """
        Creates an STP file to find a characteristic for Qarma with
        the given parameters.
        """
        self.setupComponents(stp_filename, parameters)

        # read out the parameters defining the cipher

        self.wordsize            = parameters["wordsize"]
        self.parameter           = parameters["parameter"]
        self.roundsF             = parameters["roundsF"]
        self.roundsB             = parameters["roundsB"]
        self.zerocells           = parameters["zerocells"]
        self.forcecellsfront     = parameters["forcecellsfront"]
        self.forcecellsback      = parameters["forcecellsback"]
        self.zerocellsfront      = parameters["zerocellsfront"]
        self.zerocellsback       = parameters["zerocellsback"]
        self.zerocellsback       = parameters["zerocellsback"]
        self.backsegmentweight   = parameters["backsegmentweight"]
        self.backsegmentlength   = parameters["backsegmentlength"]
        self.weightfunction      = parameters["weightfunction"]
        self.custom              = parameters["custom"]
        self.customfile          = parameters["customfile"]
        weight                   = parameters["sweight"]

        # this is to have a bound on the number of cells active at the beginning of the
        # initial/extended characteristic
        self.cellnumber          = parameters["cellnumber"]
        self.frontconecellnumber = parameters["frontconecellnumber"]

        # this is to have a bound on the number of cells active at the center
        self.centercellnumber    = parameters["centercellnumber"]

        # compute the key recovery rounds
        self.addrecovery         = parameters["addrecovery"]

        assert parameters["tweaks"] == 1, "Only one tweak is required for QarmaV1"
        assert self.parameter >= self.roundsF - 1, "parameter should be greater than or equal to roundsF-1"
        assert self.parameter >= self.roundsB - 1, "parameter should be greater than or equal to roundsB-1"

        with open(stp_filename, 'w') as stp_file:
            header = ("% Input File for STP\n% {}\n\n".format(parameters["config"]))
            stp_file.write(header)

            # ######################################################################################
            #
            # Setup variables
            #
            # State is represented as nibbles as in the QARMA(v1) paper

            # Variables for the forward rounds of the core characteristic
            # FSC--(AddTweak) --> FAT--(Permute) --> FPM--(MixCol) --> FMC--(Sbox) --> FSC[next round]

            if verbose:
                print("Creating forward round variables for core characteristic.")
            fsc = self.declareVariables(self.roundsF + 1, "FSC", stp_file)
            fat = self.declareVariables(self.roundsF, "FAT", stp_file)
            fpm = self.declareVariables(self.roundsF + 1, "FPM", stp_file)
            fmc = self.declareVariables(self.roundsF, "FMC", stp_file)
            fwn = self.declareVariables(self.roundsF, "FWN", stp_file)

            if self.addrecovery:
                # Variables for the forward key recovery characteristic rounds (computed backwards)
                # FSC[0]->fDCSC[last];  FSC/fDCSC[next_round]--Permute^(-1) --> fDCMC[round]--matrix
                # -->  fDCPM--permute --> fDCAT--(AddTweak) --> fDCSC
                # These are just single bits ones, so we do not take into account the very first tweak addition and
                # it has to be recovered in the LaTeX
                #
                # The last one is a "translation" of the first fsc from wordsize to 1 bit

                fDClast = self.parameter+1-self.roundsF
                if fDClast > 0:
                    if verbose:
                        print("Creating variables for forward key recovery characteristic.")
                    fDCsc   = self.declareSingleBitVariables(fDClast + 1, "fDCSC", stp_file)
                    fDCat   = self.declareSingleBitVariables(fDClast,     "fDCAT", stp_file)
                    fDCpm   = self.declareSingleBitVariables(fDClast - 1, "fDCPM", stp_file)
                    fDCmc   = self.declareSingleBitVariables(fDClast - 1, "fDCMC", stp_file)

            # Variables for the backward rounds of the core characteristic
            # BSC--(AddTweak)-->BAT--(Permute)-->BPM --(MixCol)-->BMC--(Sbox)-->BSC[next round]

            if verbose:
                print("Creating backward round variables for core characteristic.")

                bsc = self.declareVariables(self.roundsB + 1, "BSC", stp_file)
                bat = self.declareVariables(self.roundsB, "BAT", stp_file)
                bwn = self.declareVariables(self.roundsB, "BWN", stp_file)

            if self.addrecovery:
                # Variables for the backward key recovery characteristic rounds
                #     BSC[0]->bDCSC[last;  bDCSC[next_round]--Permute^(-1) --> fDCMC[round]--matrix -->
                #        fDCPM--permute --> fDCAT--(AddTweak) --> fDCSC
                # These are just single bits ones, so we do not take into account the very first
                #  tweak addition.

                bDClast = self.parameter+1-self.roundsB
                if bDClast > 0:
                    if verbose:
                        print("Creating variables for backward key recovery characteristic.")
                    bDCsc = self.declareSingleBitVariables(self.parameter+1-self.roundsB + 1, "bDCSC", stp_file)
                    bDCat = self.declareSingleBitVariables(self.parameter+1-self.roundsB,     "bDCAT", stp_file)
                    bDCpm = self.declareSingleBitVariables(self.parameter+1-self.roundsB - 1, "bDCPM", stp_file)
                    bDCmc = self.declareSingleBitVariables(self.parameter+1-self.roundsB - 1, "bDCMC", stp_file)

            bpm = self.declareVariables(self.roundsB + 1, "BPM", stp_file)
            bmc = self.declareVariables(self.roundsB, "BMC", stp_file)

            # Tweak Schedule

            ft,bt,tweakCommand = self.tweakSchedule(parameters, stp_file)

            stp_file.write(tweakCommand)

            self.VAR = {}

            self.VAR["fsc"] = fsc
            self.VAR["fat"] = fat
            self.VAR["fpm"] = fpm
            self.VAR["fmc"] = fmc
            self.VAR["fwn"] = fwn

            self.VAR["bsc"] = bsc
            self.VAR["bat"] = bat
            self.VAR["bpm"] = bpm
            self.VAR["bmc"] = bmc
            self.VAR["bwn"] = bwn

            if self.addrecovery:
                if fDClast > 0:
                    self.VAR["fDCsc"] = fDCsc
                    self.VAR["fDCat"] = fDCat
                    self.VAR["fDCpm"] = fDCpm
                    self.VAR["fDCmc"] = fDCmc

                if bDClast > 0:
                    self.VAR["bDCsc"] = bDCsc
                    self.VAR["bDCat"] = bDCat
                    self.VAR["bDCpm"] = bDCpm
                    self.VAR["bDCmc"] = bDCmc

            self.VAR["ft" ] = ft
            self.VAR["bt" ] = bt

            if self.addrecovery:

                if fDClast > 0:
                    stp_file.write("\n% Compute last fDCsc\n")
                    if verbose:
                        print("Compute fDCsc[{}] from fsc[0].".format(self.parameter+1-self.roundsF))
                    stp_file.write(stpcommands.getWordOrForAllState(fDCsc[self.parameter+1-self.roundsF],fsc[0], self.wordsize))

                if bDClast > 0:
                    stp_file.write("\n% Compute last bDCsc\n")
                    if verbose:
                        print("Compute bDCsc[{}] from bsc[0].".format(self.parameter+1-self.roundsB))
                    stp_file.write(stpcommands.getWordOrForAllState(bDCsc[self.parameter+1-self.roundsB],bsc[0], self.wordsize))

            wn = []
            for l in fwn:
                wn += l
            for l in bwn:
                wn += l

            # ######################################################################################
            #
            # Set up the weight function / cost function
            #
            # It is a different one according whether the CD is extended to a KRC.

            if  (not self.addrecovery) or (fDClast == 0):
                stpcommands.setupWeightComputation(stp_file, weight, wn, self.wordsize)
            elif fDClast > 0:
                if (self.weightfunction == 0):
                    if verbose:
                        print("Forcing weight function = p")
                    stpcommands.setupWeightComputation(stp_file, weight, wn, self.wordsize)
                else:
                    stp_file.write("KRcost: BITVECTOR(16);\n")
                    stp_file.write("weight: BITVECTOR(16);\n")
                    stpcommands.setupWeightComputation(stp_file, -1, wn, self.wordsize, weightVariable="distweight",vectorLength=16)
                    stpcommands.setupWeightComputation(stp_file, -1, fDCsc[0], 1, weightVariable="DinWeight",vectorLength=16)
                    stp_file.write("ASSERT(weight = BVPLUS(16,distweight,(DinWeight << 2)[15:0]));\n")

                stp_file.write("ASSERT(weight = {0:#018b});\n".format(weight))

            if self.cellnumber != -1:
                if verbose:
                    print("Setting up cellnumber")
                stp_file.write("cellnumber: BITVECTOR(5);\n")
                stpcommands.setupWeightComputationCell(stp_file,self.cellnumber,fsc[0],self.wordsize,weightVariable="cellnumber")

            if self.centercellnumber != -1:
                if verbose:
                    print("Setting up center cellnumber")
                stp_file.write("centercellnumberF: BITVECTOR(5);\n")
                stpcommands.setupWeightComputationCell(stp_file,self.centercellnumber,fsc[self.roundsF],self.wordsize,weightVariable="centercellnumberF")
                stp_file.write("centercellnumberB: BITVECTOR(5);\n")
                stpcommands.setupWeightComputationCell(stp_file,self.centercellnumber,bsc[self.roundsB],self.wordsize,weightVariable="centercellnumberB")

            if self.frontconecellnumber != -1:
                if verbose:
                    print("Setting up frontconecellnumber")
                stp_file.write("frontconecellnumber: BITVECTOR(5);\n")
                stpcommands.setupWeightComputationCell(stp_file,self.frontconecellnumber,fDCsc[0],1,weightVariable="frontconecellnumber")

            if self.backsegmentweight != None:
                if verbose:
                    print("Setting up back segment weight")
                stp_file.write("backsegmentweight: BITVECTOR(5);\n")
                stpcommands.setupWeightComputationCell(stp_file,
                    self.backsegmentweight,bDCsc[0][0:self.backsegmentlength],1,weightVariable="backsegmentweight")

            # ######################################################################################
            #
            # Modelling the core characteristic
            #
            # Forward rounds of the core characteristic

            tweakIndex = self.parameter - self.roundsF + 1
            for rnd in range(self.roundsF):
                if tweakIndex == 0:
                    if verbose:
                        print("Setting up short forward round {}, fsc[{}] to fsc[{}].".format(tweakIndex,rnd,rnd+1))
                    self.setupQarmaHalfRound(stp_file, fsc[0], fat[0], fsc[1], fwn[0], ft[0])
                else:
                    if verbose:
                        print("Setting up forward round {}, fsc[{}] to fsc[{}].".format(tweakIndex,rnd,rnd+1))
                    self.setupQarmaRound(stp_file, fsc[rnd], fat[rnd], fpm[rnd],
                                                   fmc[rnd], fsc[rnd+1], fwn[rnd], ft[tweakIndex])
                tweakIndex += 1

            # Backward rounds of the core characteristic

            tweakIndex = self.parameter - self.roundsB + 1
            for rnd in range(self.roundsB):
                if tweakIndex == 0:
                    if verbose:
                        print("Setting up short backward round {}, bsc[{}] to bsc[{}].".format(rnd,rnd,rnd+1))
                    self.setupQarmaHalfRound(stp_file, bsc[0], bat[0], bsc[1], bwn[0], bt[0])
                else:
                    if verbose:
                        print("Setting up backward round {}, bsc[{}] to bsc[{}].".format(rnd,rnd,rnd+1))
                    self.setupQarmaRound(stp_file, bsc[rnd], bat[rnd], bpm[rnd],
                                                   bmc[rnd], bsc[rnd+1], bwn[rnd], bt[tweakIndex])
                tweakIndex += 1

            # Middle round of the core characteristic

            if verbose:
                print("Setting up middle round, fsc[{}] to bsc[{}].".format(self.roundsF,self.roundsB))
            self.setupQarmaMiddleRound(stp_file, fsc[self.roundsF], fpm[self.roundsF], bpm[self.roundsB], bsc[self.roundsB])

            if self.addrecovery:

                # ######################################################################################
                #
                # Now that the core characteristic has been programmed, let us output
                # the description of the Key Recovery Characteristic
                # the letters DC mean Diffusion Cone
                # the letters BW mean Bit-Wise version of the Diffusion Cone

                # Backtrack the forward rounds of the Key Recovery Characteristic

                if fDClast > 0:

                    stp_file.write("\n% backtrack key recovery characteristic, forward rounds\n")

                    for i in range(1,self.parameter+1-self.roundsF):
                        rnd = self.parameter+1-self.roundsF - i
                        if verbose:
                            print("Setting up forward key recovery (reversed) round {}, fDCsc[{}] to fDCsc[{}].".format(rnd,rnd+1,rnd))

                        self.setupCellwiseInverseQarmaRound(stp_file, fDCsc[rnd], fDCat[rnd], fDCpm[rnd-1], fDCmc[rnd-1], fDCsc[rnd+1], ft[rnd], False)

                    if verbose:
                        print("Setting up forward key recovery (reversed) round 0, fDCsc[1] to fDCsc[0].")

                    self.setupCellwiseInverseQarmaRound(stp_file, fDCsc[0], fDCat[0], '', '',
                                                                  fDCsc[1], ft[0], True)

                # Compute the backward rounds of the the Key Recovery Characteristic
                # (exact same steps of the backtracking of the forward rounds, since the latter are done
                # inverted.

                if bDClast > 0:

                    stp_file.write("\n% complete key recovery characteristic, backward rounds\n")

                    for i in range(1,self.parameter+1-self.roundsB):
                        rnd = self.parameter+1-self.roundsB - i
                        if verbose:
                            print("Setting up backward key recovery round {}, bDCsc[{}] to bDCsc[{}].".format(rnd,rnd+1,rnd))
                        self.setupCellwiseInverseQarmaRound(stp_file, bDCsc[rnd],   bDCat[rnd], bDCpm[rnd-1], bDCmc[rnd-1],
                                                                      bDCsc[rnd+1], bt[rnd], False)

                    if verbose:
                        print("Setting up backward key recovery round 0, bDCsc[1] to bDCsc[0].")
                    self.setupCellwiseInverseQarmaRound(stp_file, bDCsc[0], bDCat[0], '', '',
                                                                  bDCsc[1], bt[0], True)

                # Constraint on the beginning of the CC§

                if fDClast > 0:
                    stp_file.write("\n% Constraint on the beginning of the CD\n")
                    stpcommands.assertNonZero(stp_file, fDCsc[fDClast], 1)

                # Constraints at beginning of KRC, i.e. input clamping (includes tweak)
                # and zero cells at front and back (does not include tweak)

                if fDClast > 0:
                    if self.zerocells:
                        if verbose:
                            print("Setting up zerocellsnumber(front)")
                        stp_file.write("\n% Constraints on zerocells\n")
                        for i in range(self.zerocells):
                            stpcommands.assertVariableValue(stp_file, fDCsc[0][i], '0b0')
                            if ft[0] != []:
                                stpcommands.assertVariableValue(stp_file, ft[0][i], '0b0000')

                if fDClast > 0:
                    if self.zerocellsfront:
                        if verbose:
                            print("Setting up zerocellsfront")
                        for ss in self.zerocellsfront:
                            stp_file.write(f"\n% Constraints on zero cells at front of KRC: {ss}\n")
                            variables = [fDCsc[0][i] for i in ss]
                            stpcommands.assertAZero(stp_file, variables, 1)

                if bDClast > 0:
                    if self.zerocellsback:
                        if verbose:
                            print("Setting up zerocellsback")
                        for ss in self.zerocellsback:
                            stp_file.write(f"\n% Constraints on zero cells at back of KRC: {ss}\n")
                            variables = [bDCsc[0][i] for i in ss]
                            stpcommands.assertAZero(stp_file, variables, 1)

                # Constraints for the sets of cells for which in each of them we want at least one active cell per list

                if fDClast > 0:
                    if self.forcecellsfront:
                        if verbose:
                            print("Setting up forcecellsfront")
                        for ss in self.forcecellsfront:
                            stp_file.write(f"\n% Constraints on forced cells at front of KRC: {ss}\n")
                            variables = [fDCsc[0][i] for i in ss]
                            stpcommands.assertNonZero(stp_file, variables, 1)

                if bDClast > 0:
                    if self.forcecellsback:
                        if verbose:
                            print("Setting up forcecellsback")
                        for ss in self.forcecellsback:
                            stp_file.write(f"\n% Constraints on forced cells at back of KRC: {ss}\n")
                            variables = [bDCsc[0][i] for i in ss]
                            stpcommands.assertNonZero(stp_file, variables, 1)

            # #####################################################################################
            #
            # Exclude the all zero characteristic

            stp_file.write("\n% Exclude the all zero characteristic\n")
            stpcommands.assertNonZero(stp_file, fsc[0]+ft[0], self.wordsize)

            for key, value in parameters["fixedVariables"].items():
                stpcommands.assertVariableValue(stp_file, key, value)

            for char in parameters["blockedCharacteristics"]:
                stpcommands.blockCharacteristic(stp_file, char, self.wordsize)

            # #####################################################################################
            #
            # Add custom commands

            if self.custom:
                stp_file.write("\n% Custom command(s)\n")
                stp_file.write(self.custom)
                stp_file.write("\n")

            if self.customfile:
                stp_file.write("\n% Custom command(s)\n")
                with open(self.customfile, 'r') as in_f:
                    for line in in_f:
                        stp_file.write(line)
                stp_file.write("\n")

            # #####################################################################################
            #
            # Set up query

            stp_file.write("\n")
            stp_file.write("\n% Query\n")
            stpcommands.setupQuery(stp_file)

        return

    def permuteCell(self, A, S):
        B = [0 for i in range(16)]
        for cell in range(16):
            B[cell] = A[S[cell]];
        return B

    def mixColumn(self, A, B):
        RA = self.ROT[0]
        RB = self.ROT[1]
        RC = self.ROT[2]

        command = ""
        for c in range(4): #for each column

            #0th cell
            ci = [c + 4*1, c + 4*2, c + 4*3]
            # print(ci)
            for j in range(4): #for each bit of the 0th cell
                bi = [(j+4-RA)%4, (j+4-RB)%4, (j+4-RC)%4]

                s = "ASSERT(BVXOR(BVXOR"
                s += "({0}[{1}:{1}], {2}[{3}:{3}]), {4}[{5}:{5}]) = {6}[{7}:{7}]);\n"\
                .format(A[ci[0]], bi[0], A[ci[1]], bi[1], A[ci[2]], bi[2], B[c + 4*0], j)

                command += s

            #1st cell
            ci = [c + 4*0, c + 4*2, c + 4*3]
            # print(ci)
            for j in range(4): #for each bit of the 1st cell
                bi = [(j+4-RC)%4, (j+4-RA)%4, (j+4-RB)%4]
                s = "ASSERT(BVXOR(BVXOR"
                s += "({0}[{1}:{1}], {2}[{3}:{3}]), {4}[{5}:{5}]) = {6}[{7}:{7}]);\n"\
                .format(A[ci[0]], bi[0], A[ci[1]], bi[1],A[ci[2]], bi[2], B[c + 4*1], j)

                command += s

            #2nd cell
            ci = [c + 4*0, c + 4*1, c + 4*3]
            # print(ci)
            for j in range(4): #for each bit of the 2nd cell
                bi = [(j+4-RB)%4, (j+4-RC)%4, (j+4-RA)%4]
                s = "ASSERT(BVXOR(BVXOR"
                s += "({0}[{1}:{1}], {2}[{3}:{3}]), {4}[{5}:{5}]) = {6}[{7}:{7}]);\n"\
                .format(A[ci[0]], bi[0], A[ci[1]], bi[1], A[ci[2]], bi[2], B[c + 4*2], j)

                command += s

            #3rd cell
            ci = [c + 4*0, c + 4*1, c + 4*2]
            # print(ci)
            for j in range(4): #for each bit of the 3rd cell
                bi = [(j+4-RA)%4, (j+4-RB)%4, (j+4-RC)%4]
                s = "ASSERT(BVXOR(BVXOR"
                s += "({0}[{1}:{1}], {2}[{3}:{3}]), {4}[{5}:{5}]) = {6}[{7}:{7}]);\n"\
                .format(A[ci[0]], bi[0], A[ci[1]], bi[1],A[ci[2]], bi[2], B[c + 4*3], j)

                command += s

        return command

    def setupQarmaRound(self, stp_file, sc_in, at, pm, mc, sc_out, wn, T):
        """
        Model for differential behaviour of one forward round Qarma.
        """
        command = ""
        #add Tweak
        for cell in range(16):
            command += "ASSERT(BVXOR({0},{1}) = {2});\n".format(sc_in[cell],T[cell],at[cell])

        temp = self.permuteCell(at, self.TAU)
        for cell in range(16):
            command += "ASSERT({0} = {1});\n".format(temp[cell], pm[cell])

        # MixColumns
        command += self.mixColumn(pm, mc)

        for sbox in range(16):
            command += stpcommands.add4bitSboxNibbles(self.sbox, mc[sbox], sc_out[sbox], wn[sbox])

        stp_file.write(command)

        return

    def setupQarmaHalfRound(self, stp_file, sc_in, at, sc_out, wn, T):
        """
        Model for differential behaviour of one forward round Qarma.
        """
        command = ""
        #add Tweak
        if T == []:
            for cell in range(16):
                command += "ASSERT({0} = {1});\n".format(sc_in[cell],at[cell])
        else:
            for cell in range(16):
                command += "ASSERT(BVXOR({0},{1}) = {2});\n".format(sc_in[cell],T[cell],at[cell])

        for sbox in range(16):
            command += stpcommands.add4bitSboxNibbles(self.sbox,at[sbox],sc_out[sbox],wn[sbox])

        stp_file.write(command)

        return

    def setupQarmaMiddleRound(self, stp_file, sc_in, pm_in, pm_out, sc_out):
        """
        Middle round of Qarma.
        sc_roundsF --permuteCell--> temp1 --> M <-- temp2 <--permuteCell-- sc_roundsB
        """

        command = ""
        temp1 = self.permuteCell(sc_in, self.TAU)
        for cell in range(16):
            command += "ASSERT({0} = {1});\n".format(temp1[cell], pm_in[cell])

        temp2 = self.permuteCell(sc_out, self.TAU)
        for cell in range(16):
            command += "ASSERT({0} = {1});\n".format(temp2[cell], pm_out[cell])

        command += self.mixColumn(pm_in, pm_out)

        stp_file.write(command)
        return


    def setupCellwiseInverseQarmaRound(self, stp_file, sc_in, at, pm, mc, sc_out, T, isShort):
        """
        Model for truncated differential behaviour of one forward round Qarma, from start of core characteristic to key recover characteristic
        This one works backwards in order to have the correct diffusion through the matrix
        """
        command = ""
        if not isShort:

            # S-Box, sc_out -> mc
            for cell in range(16):
                command += "ASSERT({0} = {1});\n".format(mc[cell],sc_out[cell])

            # Matrix, , sc_out -> pm
            for column in range(4):
                for output_row in range(4):
                    subcommand = ""
                    for input_row in range(4):
                        if input_row != output_row:
                            subcommand += "{0}|".format(mc[column+4*input_row])
                    subcommand = subcommand[:-1]
                    command += "ASSERT({0} = {1});\n".format(pm[column+4*output_row],subcommand)

            # shuffle cells, should work on any size, including single bit?
            temp = self.permuteCell(at, self.TAU)
            for cell in range(16):
                command += "ASSERT({0} = {1});\n".format(temp[cell], pm[cell])

            # addtweak, at + T -> sc_in
            for cell in range(16):
                temp = stpcommands.getWordOr(T[cell], self.wordsize)
                command += "ASSERT({0} = {1}|{2});\n" .format(sc_in[cell],temp,at[cell])
        else:

            # S-Box, sc_out -> at
            for cell in range(16):
                command += "ASSERT({0} = {1});\n".format(at[cell],sc_out[cell])

            # SKIP the addtweakm in first (and last) round
            for cell in range(16):
                command += "ASSERT({0} = {1});\n".format(sc_in[cell],at[cell])

        stp_file.write(command)

        return


    def equal(self, t1, t2):
        command = "ASSERT({0} = {1}); \n".format(t1, t2)
        return command


    def setSomeCellsZero(self, stp_file, V, cells):
        command = ""
        for cell in cells:
            command += "ASSERT({} = 0x0);\n".format(V[cell])
        stp_file.write(command)


    def excludeChar(self, parameters, characteristic):
        parameters["blockedCharacteristics"] += [characteristic]
        # print(parameters["blockedCharacteristics"])


    def excludeDiff(self, parameters, characteristic):
        theDict  = self.getExData(characteristic, 0, "ft")
        theDict |= self.getExData(characteristic, 0, "fsc")
        # theDict |= self.getExData(characteristic, 0, "bsc")
        print("excluding", theDict)
        parameters["blockedCharacteristics"] += [theDict]
        # print(parameters["blockedCharacteristics"])


    def getExData(self, characteristic, rnd, name):
        var = self.VAR[name][rnd]
        data = {}

        for col in range(4):
            for row in range(4):
                v = var[col + (4*row)]
                if characteristic[v] != "0x0":
                    data[v] = characteristic[v]
        return data


    def printDiff(self, parameters, characteristic, weight, f):
        T = self.getStateData(characteristic, 0, "ft")
        X = self.getStateData(characteristic, 0, "fsc")
        Y = self.getStateData(characteristic,0, "bsc")
        data = [T+X+Y + [weight]]
        table = tabulate(data, tablefmt="grid")
        print(table)
        f.write(table)


    def printDiffCFormat(self, parameters, characteristic, weight):
        parameter = parameters["parameter"]
        roundsF = parameters["roundsF"]
        roundsB = parameters["roundsB"]

        s = ""
        s += "parameter = {};\n".format(parameter)
        s += "roundsF = {};\n".format(roundsF)
        s += "roundsB = {};\n".format(roundsB)

        if(parameters["cipher"] == "qarmav2"):
            s += self.getStateDataCFormat(characteristic, 1, "ft")
        else:
            s += self.getStateDataCFormat(characteristic, 0, "ft")
        s += self.getStateDataCFormat(characteristic, 0, "fsc")
        s += self.getStateDataCFormat(characteristic, 0, "bsc")
        s += self.getStateActivePat(characteristic, 0, "fsc")
        s += self.getStateActivePat(characteristic, 0, "ft")
        s += self.getStateActivePat(characteristic, 0, "bsc")

        print(s)


    def printInputPatCFormat(self, parameters, VAR):
        L = VAR["fsc"][0].split(",")
        J = parameters["parameter"] - parameters["roundsF"]
        if J == 0:
            L = self.sboxTruncated(L)
        for j in range(J):
            i = J - j
            T  = VAR["ft"][i].split(",")
            L = self.oneRoundTruncated(L, T)

        LL = ["0" for i in range(16)]

        data = []
        for i in range(16):
            if (L[i] != "0"):
                LL[i] = "0x1"
                data.append(str(i))
        s = "cell_t inputTruncatedState[16] = {" + ",".join(LL) + "};\n"
        s += "int " + "truncatedPat[" + str(len(data)) + "] = {" + ",".join(data) + "};\n"
        s += "int noTruncated = " + str(len(data)) + ";\n"

        print(s)


    def getStateDataCFormat(self, characteristic, rnd, name):
        var = self.VAR[name][rnd]
        if var == []:
            return ""
        data = []
        for i in range(16):
            v = var[i]
            data.append(characteristic[v])
        s = "cell_t " + name + "[16] = {" + ",".join(data) + "};\n"
        return s


    def getStateActivePat(self, characteristic, rnd, name):
        var = self.VAR[name][rnd]
        if var == []:
            return ""
        data = []
        count = 0
        for i in range(16):
            v = var[i]
            if(characteristic[v] != '0x0'):
                data.append(str(i))
                count +=1
        s = "int " + "inActivePat"+name + "[" + str(len(data)) + "] = {" + ",".join(data) + "};\n"
        s += "int noActive"+name+" = " + str(count) + ";\n"
        return s


    def getStateData(self, characteristic, rnd, name):
        var = self.VAR[name][rnd]
        if var == []:
            return ""
        data = [name, rnd]
        for col in range(4):
            temp = []
            for row in range(4):
                v = var[col + (4*row)]
                temp.append(characteristic[v])
            data.append(",".join(temp))
        return data


    def createYaml(self, parameters, characteristic, weight, yamlFile):
        f = open(yamlFile, 'w')
        instance = ""
        instance += "cipher: " + parameters["cipher"] + "\n"
        instance += "sweight: " + str(weight) + "\n"
        instance += "parameter: " + str(parameters["parameter"]) + "\n"
        instance += "roundsF: " + str(parameters["roundsF"]) + "\n"
        instance += "roundsB: " + str(parameters["roundsB"]) + "\n"
        instance += "tweaks: " + str(parameters["tweaks"]) + "\n"
        instance += "wordsize: " + str(parameters["wordsize"]) + "\n"
        instance += "blocksize: " + str(parameters["blocksize"]) + "\n"
        instance += "mode: " + str(2) + "\n"
        instance += "fixedVariables:"+"\n"
        instance += self.writeStateDataYaml(characteristic, 0, "ft", f)
        instance += self.writeStateDataYaml(characteristic, 0, "fsc", f)
        instance += self.writeStateDataYaml(characteristic, 0, "bsc", f)
        f.write(instance)


    def writeStateDataYaml(self, characteristic, rnd, name, f):
        var = self.VAR[name][rnd]
        data = []

        for v in var:
            u = characteristic[v]
            #if need to find cluster, comment the if loop
            if (name == "ft"):
                data.append(v + ": " + "\"" + u + "\"")
            elif (name == "fsc"):
                data.append(v + ": " + "\"" + u + "\"")
            else:
                if (u == "0x0"):
                    data.append(v + ": " + "\"" + u + "\"")
        instance = ""
        for d in data:
            instance += "- " + d + "\n"
        return instance


    def sboxTruncated(self, L):
        LL = []
        for l in L:
            if l != "0":
                LL.append("*")
            else:
                LL.append("0")
        return LL


    def rowColMul(self, R, C):
        res = "0"
        for x in range(4):
            if ((R[0] != 0) and (C[0] != "0")):
                res = "*"
            if ((R[1] != 0) and (C[1] != "0")):
                res = "*"
            if ((R[2] != 0) and (C[2] != "0")):
                res = "*"
            if ((R[3] != 0) and (C[3] != "0")):
                res = "*"
        return res


    def mixcolTruncated(self, L):
        M = [["0", "*", "*", "*"], ["*",0,"*","*"], ["*","*",0,"*"], ["*","*","*",0]]
        LL = ["0" for i in range(16)]
        for c in range(4): #operation on each column
            col = [L[c], L[4+c], L[8+c], L[12+c]]
            LL[c]    = self.rowColMul(M[0], col)
            LL[4+c]  = self.rowColMul(M[1], col)
            LL[8+c]  = self.rowColMul(M[2], col)
            LL[12+c] = self.rowColMul(M[3], col)
        return LL

    def addtweakTruncated(self, L, T):
        LL = L[:]
        for i in range(16):
            if (T[i] != "0"):
                LL[i] = "*"
        return LL


    def oneRoundTruncated(self, delta, T):
        L  = self.sboxTruncated(delta)
        # print(self.transpose(L))
        L = self.mixcolTruncated(L)
        # print(self.transpose(L))
        L = self.permuteCell(L, self.TAU_INV)
        # print(self.transpose(L))
        L = self.addtweakTruncated(L, T)
        # print(self.transpose(L))
        # L = ", ".join(L)
        return L


    def varToVal(self, parameters, characteristic):
        #print(characteristic)
        for var in self.VAR.keys():
            L = self.VAR[var]
            for i, l in enumerate(L):
                temp = []
                try:
                    for v in l:
                        temp.append(characteristic[v][2:])
                    temp = ",".join(temp)
                except:
                    continue
                L[i] = temp


    def transpose(self, L):
        LL = []
        for col in range(4):
            temp = []
            for row in range(4):
                v = L[col + (4*row)]
                LL.append(v)
        return LL


    def printSol(self, parameters, characteristic, weight, solFile, current_time):
        f = open(solFile, 'w')
        s = "---\n"
        s += "#Characteristic for {} -Weight {} Time {}s\n".\
                format(parameters["config"], parameters["sweight"] , current_time)

        f.write(s)
        parameter = parameters["parameter"]
        roundsF = parameters["roundsF"]
        roundsB = parameters["roundsB"]
        print(f'{parameter = }')
        print(f'{roundsF   = }')
        print(f'{roundsB   = }')

        # print(characteristic)
        # print(variables)
        data = [["Round","Variable", "Col0", "Col1", "Col2", "Col3"]]
        tweakIndex = 0
        for rnd in range(parameter - roundsF + 1):
            data.append(self.getStateData(characteristic, tweakIndex, "ft"))
            tweakIndex += 1
        data.append(["****", "****", "****", "****", "****", "****"])

        if self.addrecovery:
            data.append(self.getStateData(characteristic, 0, "fDCsc"))
            if (self.parameter != self.roundsF):
                data.append(self.getStateData(characteristic, 1, "fDCat"))
            data.append(self.getStateData(characteristic, 1, "fDCsc"))
            for rnd in range(self.parameter-self.roundsF):
                data.append(self.getStateData(characteristic, rnd+1, "fDCat"))
                data.append(self.getStateData(characteristic, rnd, "fDCpm"))
                data.append(self.getStateData(characteristic, rnd, "fDCmc"))
                data.append(self.getStateData(characteristic, rnd+2, "fDCsc"))
                data.append(["****", "****", "****", "****", "****", "****"])

        for rnd in range(roundsF):
            data.append(self.getStateData(characteristic, rnd, "fsc"))
            data.append(self.getStateData(characteristic, tweakIndex, "ft"))
            data.append(self.getStateData(characteristic, rnd, "fat"))
            data.append(self.getStateData(characteristic, rnd, "fpm"))
            data.append(self.getStateData(characteristic, rnd, "fmc"))
            data.append(self.getStateData(characteristic, rnd, "fwn"))
            tweakIndex += 1

        data.append(["****", "****", "****", "****", "****", "****"])
        data.append(self.getStateData(characteristic, roundsF, "fsc"))
        data.append(self.getStateData(characteristic, roundsF, "fpm"))
        data.append(self.getStateData(characteristic, roundsB, "bpm"))
        data.append(self.getStateData(characteristic, roundsB, "bsc"))
        data.append(["****", "****", "****", "****", "****", "****"])

        dataB = []
        tweakIndex = 0
        bscIndex = 0
        if parameter == roundsB - 1:
            dataB.append(self.getStateData(characteristic, bscIndex, "bsc"))
            dataB.append(self.getStateData(characteristic, tweakIndex, "bt"))
            dataB.append(self.getStateData(characteristic, bscIndex, "bat"))
            dataB.append(self.getStateData(characteristic, bscIndex, "bwn"))
            tweakIndex = 1
            bscIndex = 1
        else:
            for rnd in range(parameter - roundsB + 1):
                data.append(self.getStateData(characteristic, tweakIndex, "bt"))
                tweakIndex += 1

        dataB.append(["****", "****", "****", "****", "****", "****"])

        for rnd in range(roundsB):
            dataB.append(self.getStateData(characteristic, bscIndex, "bsc"))
            dataB.append(self.getStateData(characteristic, tweakIndex, "bt"))
            dataB.append(self.getStateData(characteristic, bscIndex, "bat"))
            dataB.append(self.getStateData(characteristic, rnd, "bpm"))
            dataB.append(self.getStateData(characteristic, rnd, "bmc"))
            dataB.append(self.getStateData(characteristic, bscIndex, "bwn"))
            tweakIndex += 1
            bscIndex += 1

        dataB.reverse()
        data += dataB

        dataB = []
        if self.addrecovery:
            data.append(self.getStateData(characteristic, 0, "bDCsc"))
            if (self.parameter != self.roundsB):
                data.append(self.getStateData(characteristic, 1, "bDCat"))
            data.append(self.getStateData(characteristic, 1, "bDCsc"))
            for rnd in range(self.parameter-self.roundsB):
                dataB.append(self.getStateData(characteristic, rnd+1, "bDCat"))
                dataB.append(self.getStateData(characteristic, rnd, "bDCpm"))
                dataB.append(self.getStateData(characteristic, rnd, "bDCmc"))
                dataB.append(self.getStateData(characteristic, rnd+2, "bDCsc"))
            data += dataB

        table = tabulate(data, headers="firstrow", tablefmt="grid")
        f.write(table)
