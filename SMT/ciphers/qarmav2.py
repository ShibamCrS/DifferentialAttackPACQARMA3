'''
Created on Jan 1, 2024

@author: XXXXXX
@author: XXXXXX
'''

from ciphers.qarmabase import QarmaBase

from parser import stpcommands
from tabulate import tabulate

class QarmaCipher(QarmaBase):
    name = "qarmav2"

    def setupComponents(self, stp_filename, parameters):
        #Sboxes
        self.R14 = [4, 7, 9,11,  12, 6,14,15,   0, 5, 1,13,   8, 3, 2,10]
        self.sigma0 = [0, 14, 2,10,   9,15, 8,11,   6, 4, 3, 7,  13,12, 1, 5]
        self.sbox = self.R14[:]
        #Permutations
        self.TAU      = [ 0,11, 6,13,   10, 1,12, 7,    5,14, 3, 8,   15, 4, 9, 2 ];
        self.TAU_INV  = [ 0, 5,15,10,   13, 8, 2, 7,   11,14, 4, 1,    6, 3, 9,12 ];
        #Tweak permutation
        self.TWEAK_TAU2F     = [ 1,10,14, 6,    2, 9,13, 5,    0, 8,12, 4,    3,11,15, 7];
        self.TWEAK_TAU2F_INV = [ 8, 0, 4,12,   11, 7, 3,15,    9, 5, 1,13,   10, 6, 2,14 ];
        self.TWEAK_P     = self.TWEAK_TAU2F
        self.TWEAK_P_INV = self.TWEAK_TAU2F_INV

        #MC ROT
        self.ROT = [1, 2, 3]

    def tweakSchedule(self, parameters, stp_file):

        def forwardTweakSchedule(self, parameters, stp_file):
            T = []
            if parameters["tweaks"] == 1:
                T0 = ["{}{}".format("T", j) for j in range(16)]
                T1 = self.permuteCell(T0, self.TWEAK_P)
                stpcommands.setupVariables(stp_file, T0, self.wordsize)
            if parameters["tweaks"] == 2:
                T0 = ["{}{}".format("TO", j) for j in range(16)]
                T1 = ["{}{}".format("TI", j) for j in range(16)]
                stpcommands.setupVariables(stp_file, T0, self.wordsize)
                stpcommands.setupVariables(stp_file, T1, self.wordsize)

            for i in range(1, self.parameter):
                T0 = self.permuteCell(T0, self.TWEAK_P )

            for i in range(self.parameter):
                # print(T1)
                # print(T0)
                if i%2 == 0:
                    temp = T1[:]
                    T.append(temp)
                    T1 = self.permuteCell(T1, self.TWEAK_P)
                if i%2 == 1:
                    temp = T0[:]
                    T.append(temp)
                    T0 = self.permuteCell(T1, self.TWEAK_P_INV)
            T = [[]] + T
            return T

        def backwardTweakSchedule(self, parameters, stp_file):
            T = []
            if parameters["tweaks"] == 1:
                T0 = ["{}{}".format("T", j) for j in range(16)]
                T1 = self.permuteCell(T0, self.TWEAK_P)
            if parameters["tweaks"] == 2:
                T0 = ["{}{}".format("TO", j) for j in range(16)]
                T1 = ["{}{}".format("TI", j) for j in range(16)]

            for i in range(1, self.parameter):
                T1 = self.permuteCell(T1, self.TWEAK_P )

            for i in range(self.parameter):
                if i%2 == 0:
                    temp = T0[:]
                    T.append(temp)
                    T0 = self.permuteCell(T0, self.TWEAK_P)
                if i%2 == 1:
                    temp = T1[:]
                    T.append(temp)
                    T1 = self.permuteCell(T1, self.TWEAK_P_INV)
            T = [[]] + T
            return T

        return forwardTweakSchedule(self, parameters, stp_file), backwardTweakSchedule(self, parameters, stp_file),""
