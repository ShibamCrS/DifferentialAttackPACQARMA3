#!/usr/bin/env python3

from tabulate import tabulate
# from keyRecovery import KeyRecovery, processSTPsolution
import random
import numpy as np
import math

def testKeyRecovery1(parameter, roundsF, roundsB, lasthalf, weight, VAR):
    visible = 16
    structs = 16
    ss = (visible + structs) * random.randint(1, 1000)
    s = KeyRecovery(parameter, roundsF, roundsB, weight, lasthalf, VAR, structs, visible, ss, 16)
    print(s)

def testKeyRecovery(parameter, roundsF, roundsB, lasthalf, weight, VAR):
    filename = "tab_"+str(parameter)+str(roundsF)+str(roundsB) + ".txt"
    filename1 = "data_"+str(parameter)+str(roundsF)+str(roundsB) + ".txt"
    fp = open(filename, "w")
    fp.close()
    fp1 = open(filename1, "w")
    fp1.close()
    data = [["Visible Cells From MSB", "No. of Structs", "Success Rate"]]
    visibles = [16, 14, 12, 10, 8, 6, 4, 3, 2]
    # visibles = [8, 6, 4, 3, 2, 1]
    #structss = [1,2,4, 8, 16, 32, 64, 128, 256]
    structss = [8,12,16,20, 24,32]
    # structss = [32, 64, 128, 256]
    EXP = 100

    if parameter == 3:
        EXP = 32
        structss = [4, 8, 16, 32, 64]
        # structss = [32, 64, 128, 192, 256]

    for visible in visibles:
        for structs in structss:
            fp1 = open(filename1, "a")
            header = "vs " + str(visible) + " " + str(structs) + "\n"
            fp1.write(header)
            fp1.close()
            A = []
            A.append(visible)
            A.append(structs)
            s = 0
            for i in range(EXP):
                print(".",end='',flush=True)
                ss = (visible + structs + i) * 1000 + random.randint(1, 1000)
                res = KeyRecovery(parameter, roundsF, roundsB, weight, lasthalf, VAR, structs, visible, ss, 16)
                kr = res[0]
                if kr > 0:
                    s += 1
                print(kr,end="",flush=True)
                fp1 = open(filename1, "a")
                res_str = [str(x) for x in res]
                res = ",".join(res_str) 
                fp1.write(res + "\n")
                fp1.close()
                # print("=>" , res)

            print("")
            A.append(s/EXP)
            aa = str(A) + "\n"
            fp = open(filename, "a")
            fp.write(aa)
            fp.close()
            print(aa)
            data.append(A)

            if (s/EXP >= 0.95):
                break
    print("",flush=True)
    table = tabulate(data, headers="firstrow", tablefmt="grid")
    fp = open(filename, "a")
    fp.write(table)
    fp.close()

    print(table)

def countNonZero(L):
    L = L.split(",")
    I = [int(x, 16) for x in L]
    Z = 0
    for i in I:
        if i > 0:
            Z = Z + 1
    return Z

def activeKey(K):
    Z = 0
    for k in K:
        Z = Z + countNonZero(k)
    Z = Z*4
    return Z

def analyzeExperimentData(data, r):
    res = {}
    res['v'] = data[0][0]
    res['s'] = data[0][1]
    data = data[1:]

    threasholdF = 256
    threasholdB = 32
    if r == 3:
        threasholdB = 128

    GP = 0
    successF = 0
    successB = 0
    for d in data:
        GP += d[1]
        if d[2] <= threasholdF:
            successF += 1
        if d[3] <= threasholdB:
            successB += 1
    exp = len(data)
    res['exp'] = exp
    res['avgGP'] = round(math.log(GP / exp, 2), 2)
    res['avgSF'] = round(successF / exp, 2)
    res['avgSB'] = round(successB / exp, 2)
    return res

def readExperimentData(filename, r):
    data = []
    res = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line: 
                continue
            if line.startswith('vs'):
                if len(res) == 0:   
                    exp = line.split(" ")
                    exp = exp[1:]
                    ints = [int(x, 10) for x in exp]
                    res.append(ints)
                    continue
                else:
                    res1 = analyzeExperimentData(res, r)
                    data.append(res1)
                    res = []
                    exp = line.split(" ")
                    exp = exp[1:]
                    ints = [int(x, 10) for x in exp]
                    res.append(ints)
                    continue
            exp = line.split(",")
            ints = [int(x, 10) for x in exp]
            res.append(ints)

    return data

def getDataKRC(VAR, r, rF, rB, weight):
    data = {}
    #Parameter
    data['r'] = r
    data['rF'] = rF
    data['rB'] = rB
    
    din = 4*countNonZero(VAR['fDCsc'][0])
    data['din'] = din
    deltain = countNonZero(VAR['fsc'][0])
    data['deltain'] = deltain
    dout = 4*countNonZero(VAR['bDCsc'][0])
    data['dout'] = dout
    p = weight - din
    data['p'] = p
    kin = activeKey(VAR["fDCsc"])
    data['kin'] = kin
    kout = activeKey(VAR["bDCsc"])
    data['kout'] = kout

    return data

def createDataTable(VAR, r, rF, rB, weight):
    data_krc = getDataKRC(VAR, r, rF, rB, weight)
    print(data_krc)
    filename = "data_"+str(r)+str(rF)+str(rB) + ".txt"
    data_experiment = readExperimentData(filename, r)
    data = [["$v$","\\rotatebox{60}{$ \\log_2 s$ }","\\rotatebox{60}{ $\\log_2 \\gamma$ }","\\rotatebox{60}{ $\\log_2 N$ }","\\rotatebox{60}{ $\\log_2 L$ }","\\rotatebox{60}{ $\\log_2 \\mathbb{D}$ }","$\\mathbb{T}$","$\\alpha$","$\\beta$"]]
    
    din = data_krc['din']    
    deltain = 0 #data_krc['deltain']    
    dout = data_krc['dout']    
    p = data_krc['p']    

    for d in data_experiment:
        print(d)
        v = d['v']
        s = round(math.log(d['s'], 2), 2)     #actually log(number of structures)
        gamma = din + deltain + s - p
        N = 2*din + s
        agp = d['avgGP']
        # egp = N - 64 + dout
        D = s + din + 1
        T = "$2^{" + str(D) + "}T_{\\calE} + " + "2^{" + str(N) + "}T_{\\textit{MR}} + " + "2^{" + str(agp) + "}T_{\\mathit{KR}}$"
        alpha = d['avgSF']
        beta  = d['avgSB']
        dd = [v, s, gamma, N, agp, D, T, alpha, beta]
        data.append(dd)
        print(dd)
    
    print(f'{din = }')
    print(f'{deltain = }')
    print(f'{p = }')
    print(f'{dout = }')
    table = tabulate(data, headers="firstrow", tablefmt="latex_raw")
    print(table)

def readKRC(fname):
    VAR = {}
    with open(fname, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('W'):
                line = line.strip().split('|')
                weight = line[1]
                continue

            line = line.strip().split('|')
            VAR[line[0]] = line[1:]
            if VAR[line[0]] == ['']:
                VAR[line[0]] = []

    return weight, VAR

def writeKRC(weight, VAR, fname):
    print(VAR)
    f = open(fname, "w")
    s = "W|" + str(weight) + "\n"
    for key in VAR:
        if type(VAR[key]) == str:
            val = "|".join(VAR[key])
            s = s + key + "|" + val + "\n"
    f.write(s)
    f.close()

if __name__ == '__main__':

    # data = [["Parameter", "roundsF", "roundsB", "dIn", "dOut", "p", "kIn", "kOut"]]
    data = []
    VAR22 = {'fsc': ['0,0,0,0,0,9,0,0,0,0,0,0,0,0,0,3', '0,0,0,0,C,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fat': ['9,0,0,0,0,9,0,0,0,0,0,0,0,0,0,3', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fpm': ['9,0,0,0,0,0,0,0,9,0,0,0,3,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fmc': ['0,0,0,0,C,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fwn': ['0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bsc': ['6,0,0,0,0,F,0,0,0,0,0,0,0,0,0,F', '0,0,0,0,C,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bat': ['F,0,0,0,0,F,0,0,0,0,0,0,0,0,0,F', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bpm': ['F,0,0,0,0,0,0,0,F,0,0,0,F,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bmc': ['0,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bwn': ['0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fDCsc': ['0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1', '0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1'],
'fDCat': ['0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1'],
'fDCpm': [], 'fDCmc': [], 'bDCsc': ['1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1', '1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1'],
'bDCat': ['1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1'],
'bDCpm': [], 'bDCmc': [], 'ft': ['0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0', '9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,C,0,0,0,0,0,0,0,0,0,0,0'],
'bt': ['0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0', '9,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,C,0,0,0,0,0,0,0,0,0,0,0']}

    VAR12 = {'fsc': ['0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fat': ['0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fpm': ['0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fmc': ['0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fwn': ['0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bsc': ['B,0,0,0,0,8,0,0,0,0,0,0,0,0,0,1', '0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bat': ['8,0,0,0,0,8,0,0,0,0,0,0,0,0,0,1', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bpm': ['8,0,0,0,0,0,0,0,8,0,0,0,1,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bmc': ['0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bwn': ['0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fDCsc': ['1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1', '1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1', '0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0'],
'fDCat': ['1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1', '1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1'],
'fDCpm': ['1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0'],
'fDCmc': ['0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0'],
'bDCsc': ['1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1', '1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1'],
'bDCat': ['1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1'],
'bDCpm': [], 'bDCmc': [], 'ft': ['0,0,0,0,0,0,7,0,0,0,0,0,0,0,0,0', '3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0'],
'bt': ['0,0,0,0,0,0,7,0,0,0,0,0,0,0,0,0', '3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0']}

    VAR33 = {'fsc': ['0,0,9,5,0,0,0,0,0,7,0,0,D,0,0,0', '0,0,0,0,0,0,9,0,0,0,F,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fat': ['0,0,0,5,0,0,E,0,0,7,0,0,D,0,0,0', 'F,0,0,0,0,0,0,0,0,0,F,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fpm': ['0,0,E,0,0,0,D,0,0,0,5,0,0,0,7,0', 'F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fmc': ['0,0,0,0,0,0,A,0,0,0,E,0,0,0,0,0', 'F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fwn': ['0,0,0,0,0,0,7,0,0,0,3,0,0,0,0,0', '3,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bsc': ['0,0,9,A,0,0,7,0,0,C,0,0,9,0,0,0', '0,0,0,0,0,0,9,0,0,0,F,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bat': ['0,0,0,A,0,0,9,0,0,C,0,0,9,0,0,0', 'F,0,0,0,0,0,0,0,0,0,F,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bpm': ['0,0,9,0,0,0,9,0,0,0,A,0,0,0,C,0', 'F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bmc': ['0,0,0,0,0,0,5,0,0,0,C,0,0,0,0,0', 'F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bwn': ['0,0,0,0,0,0,3,0,0,0,3,0,0,0,0,0', '3,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fDCsc': ['0,0,1,1,0,0,0,0,0,1,0,0,1,0,0,0', '0,0,1,1,0,0,0,0,0,1,0,0,1,0,0,0'],
'fDCat': ['0,0,1,1,0,0,0,0,0,1,0,0,1,0,0,0'],
'fDCpm': [], 'fDCmc': [], 'bDCsc': ['0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0', '0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0'],
'bDCat': ['0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0'],
'bDCpm': [], 'bDCmc': [], 'ft': ['0,0,E,0,0,0,0,0,0,0,0,0,0,0,9,0', '0,0,9,0,0,0,E,0,0,0,0,0,0,0,0,0', 'F,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0'],
'bt': ['0,0,E,0,0,0,0,0,0,0,0,0,0,0,9,0', '0,0,9,0,0,0,E,0,0,0,0,0,0,0,0,0', 'F,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0']}
    
    VAR23 = {'fsc': ['0,0,0,0,0,0,9,0,0,0,F,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fat': ['F,0,0,0,0,0,0,0,0,0,F,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fpm': ['F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fmc': ['F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fwn': ['3,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bsc': ['0,0,9,A,0,0,7,0,0,C,0,0,9,0,0,0', '0,0,0,0,0,0,9,0,0,0,F,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bat': ['0,0,0,A,0,0,9,0,0,C,0,0,9,0,0,0', 'F,0,0,0,0,0,0,0,0,0,F,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bpm': ['0,0,9,0,0,0,9,0,0,0,A,0,0,0,C,0', 'F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bmc': ['0,0,0,0,0,0,5,0,0,0,C,0,0,0,0,0', 'F,0,0,0,F,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'bwn': ['0,0,0,0,0,0,3,0,0,0,3,0,0,0,0,0', '3,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
'fDCsc': ['0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0', '0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0', '0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0'],
'fDCat': ['0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0', '0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0'],
'fDCpm': ['0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0'],
'fDCmc': ['0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0'],
'bDCsc': ['0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0', '0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0'],
'bDCat': ['0,0,1,1,0,0,1,0,0,1,0,0,1,0,0,0'],
'bDCpm': [], 'bDCmc': [], 'ft': ['0,0,E,0,0,0,0,0,0,0,0,0,0,0,9,0', '0,0,9,0,0,0,E,0,0,0,0,0,0,0,0,0', 'F,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0'],
'bt': ['0,0,E,0,0,0,0,0,0,0,0,0,0,0,9,0', '0,0,9,0,0,0,E,0,0,0,0,0,0,0,0,0', 'F,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0', 'C,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0']}

    # s = getDataKRC(VAR22, 2, 2, 2, 13)
    # data.append(s)
    # s = getDataKRC(VAR12, 2, 1, 2, 14)
    # data.append(s)
    # s = getDataKRC(VAR33, 3, 3, 3, 35)
    # data.append(s)
    # s = getDataKRC(VAR23, 3, 2, 3, 34)
    # data.append(s)
    # # table = tabulate(data, headers="firstrow", tablefmt="grid")
    # # print(table)
    # print(data)

    # fname = "test.tex"
    # writeKRC(13, VAR22, fname)
    # weight, VAR1 = readKRC(fname)
    # print(weight)
    # assert (VAR22 == VAR1) 

    # testKeyRecovery(2, 2, 2, 0, 13, VAR22)
    # testKeyRecovery(2, 1, 2, 0, 14, VAR12)
    # testKeyRecovery(3, 3, 3, 0, 35, VAR33)
    # testKeyRecovery(3, 2, 3, 0, 34, VAR23)

    # createDataTable(VAR22, 2, 2, 2, 13)
    # createDataTable(VAR33, 3, 3, 3, 35)
    # createDataTable(VAR12, 2, 1, 2, 14)
