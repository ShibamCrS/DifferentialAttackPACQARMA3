'''
Created on Jan 1, 2024

@author: XXXXXX
@author: XXXXXX
'''

from ciphers.qarmabase import QarmaBase

from parser import stpcommands
from tabulate import tabulate

class QarmaCipher(QarmaBase):
    name = "qarmav1"

    def lfsr(self, t1, t2):
        command = ""
        for i in range(3):
            command += "ASSERT({0}[{2}:{2}] = {1}[{3}:{3}]); \n"\
                    .format(t2, t1, i, i+1)
        command += "ASSERT(BVXOR({0}[0:0], {0}[1:1]) = {1}[3:3]); \n"\
                    .format(t1, t2)
        return command

    def OMEGA(self, T1, T2):
        UC = [0, 1, 3, 4, 8, 11, 13]
        command = ""
        for i in range(16):
            if i in UC:
                command += self.lfsr(T1[i], T2[i])
            else:
                command += self.equal(T1[i], T2[i])
        return command

    def setupComponents(self, stp_filename, parameters):
        #Sboxes
        self.R14 = [4, 7, 9,11,  12, 6,14,15,   0, 5, 1,13,   8, 3, 2,10]
        self.sigma0 = [0, 14, 2,10,   9,15, 8,11,   6, 4, 3, 7,  13,12, 1, 5]
        self.sbox = self.sigma0
        #Permutations
        self.TAU      = [ 0,11, 6,13,   10, 1,12, 7,    5,14, 3, 8,   15, 4, 9, 2 ];
        self.TAU_INV  = [ 0, 5,15,10,   13, 8, 2, 7,   11,14, 4, 1,    6, 3, 9,12 ];
        #Tweak permutation
        self.TWEAK_P     = [6,5,14,15,0,1,2,3,7,12,13,4,8,9,10,11]
        self.TWEAK_P_INV = [4,5,6,7,11,1,0,8,12,13,14,15,9,10,2,3]
        #MC ROTATIONS
        self.ROT = [1, 2, 1]

    def tweakSchedule(self, parameters, stp_file):
        command = ""
        ft  = self.declareVariables(self.parameter + 1, "FT", stp_file)
        bt = self.declareVariables(self.parameter + 1, "BT", stp_file)

        for i in range(self.parameter):
            T = self.permuteCell(ft[i], self.TWEAK_P)
            command += self.OMEGA(T, ft[i+1])

        for i in range(self.parameter):
            T = self.permuteCell(bt[i], self.TWEAK_P)
            command += self.OMEGA(T, bt[i+1])
        for i in range(16):
            t1 = ft[self.parameter][i]
            t2 = bt[self.parameter][i]
            command += self.equal(t1, t2)

        return ft,bt,command
