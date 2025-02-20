#!/usr/bin/env python3
'''
Created on Feb 1, 2024

@author: XXXXXX
'''
import sys

SHUFFLE_P     = [0,11, 6,13,   10, 1,12, 7,   5,14, 3, 8,  15, 4, 9, 2]
SHUFFLE_P_inv = [0, 5,15,10,   13, 8, 2, 7,  11,14, 4, 1,   6, 3, 9,12]

TWEAKEY_P     = [ 6, 5,14,15,   0, 1, 2, 3,   7,12,13, 4,   8, 9,10,11]
TWEAKEY_P_inv = [ 4, 5, 6, 7,  11, 1, 0, 8,  12,13,14,15,   9,10, 2, 3]

def unpack(state):
    if state == "":
        return [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
    result = state.replace('A','10').replace('B','11').replace('C','12').replace('D','13').replace('E','14').replace('F','15').replace('*','-1')
    return eval('[' +result+ ']')

def applyMatrix(state):
    s = unpack(state)
    result = [0 for i in range(16)]
    for x in range(4):
        for y in range(4):
            if s[x + y*4] != 0:
                for y2 in range(4):
                    if y2 != y:
                        result[x + y2*4] = '-1'
    result = str(result)[1:][:-1].replace(' ','').replace("'",'')
    return(result)

def applyPerm(state,perm):
    result = unpack(state)
    result = [result[perm[i]] for i in range(16)]
    result = str(result)[1:][:-1].replace(' ','').replace("'",'')
    return(result)

def applySbox(state):
    result = unpack(state)
    result = [0 if result[i] == 0 else -1 for i in range(16)]
    result = str(result)[1:][:-1].replace(' ','').replace("'",'')
    return(result)

def addStates(state1,state2):
    s1 = unpack(state1)
    s2 = unpack(state2)
    result = [0 for i in range(16)]
    for i in range(16):
        if (s1[i] == -1) or (s2[i] == -1):
            result[i] = -1
        else:
            result[i] = s1[i] ^ s2[i]
    result = str(result)[1:][:-1].replace(' ','').replace("'",'')
    result = result.replace('10','A').replace('11','B').replace('12','C').replace('13','D').replace('14','E').replace('15','F')
    return(result)

def preProcessVAR(VAR, r, roundsF, roundsB):

    # the expanded forward rounds, going backwards towards the beginning of the cipher
    if roundsF < (r+1):
        for i in range(r+1-roundsF+1):
            if i == r+1-roundsF:
                VAR['fsc'] = [addStates(VAR['fat'][0],VAR['ft'][0])] + VAR['fsc']
            elif i == r+1-roundsF-1:
                if i != 0:
                    VAR['fsc'] = [addStates(VAR['fat'][0],VAR['ft'][1])] + VAR['fsc']
                VAR['fat'] = [applySbox(VAR['fsc'][0])] + VAR['fat']
            else:
                if i != 0:
                    # at creates a new fsc by applySbox
                    VAR['fsc'] = [addStates(VAR['fat'][0],VAR['ft'][r+1-roundsF-i])] + VAR['fsc']
                # fsc creates a new fmc by applySbox
                VAR['fmc'] = [applySbox(VAR['fsc'][0])] + VAR['fmc']
                # fmc creates a new fpm by applyMatrix
                VAR['fpm'] = [applyMatrix(VAR['fmc'][0])] + VAR['fpm']
                # fpm creates a new fat
                VAR['fat'] = [applyPerm(VAR['fpm'][0],SHUFFLE_P_inv)] + VAR['fat']
    else:
        VAR['fmc'] = VAR['fmc'][1:]
        VAR['fpm'] = VAR['fpm'][1:]

    # the backward rounds, we go this time with the direction of the cipher
    if roundsB < (r+1):
        for i in range(r+1-roundsB+1):
            if i == r+1-roundsB:
                VAR['bsc'] = [addStates(VAR['bat'][0],VAR['bt'][0])] + VAR['bsc']
            elif i == r+1-roundsB-1:
                if i != 0:
                    VAR['bsc'] = [addStates(VAR['bat'][0],VAR['bt'][1])] + VAR['bsc']
                VAR['bat'] = [applySbox(VAR['bsc'][0])] + VAR['bat']
            else:
                if i != 0:
                    # bat creates a new bsc by applySbox
                    VAR['bsc'] = [addStates(VAR['bat'][0],VAR['bt'][r+1-roundsB-i])] + VAR['bsc']
                # bsc creates a new bmc by applySbox
                VAR['bmc'] = [applySbox(VAR['bsc'][0])] + VAR['bmc']
                # bmc creates a new bpm by applyMatrix
                VAR['bpm'] = [applyMatrix(VAR['bmc'][0])] + VAR['bpm']
                # bpm creates a new bat
                VAR['bat'] = [applyPerm(VAR['bpm'][0],SHUFFLE_P_inv)] + VAR['bat']
    else:
        VAR['bmc'] = VAR['bmc'][1:]
        VAR['bpm'] = VAR['bpm'][1:]

    for name in ['fsc', 'bsc', 'fat', 'bat', 'fpm', 'bpm', 'fmc', 'bmc']:
        while (len(VAR[name]) < r+2):
            VAR[name] = [''] + VAR[name]

    return VAR

def createTikz(name, origVAR, r, roundsF, roundsB):

    VAR = preProcessVAR(origVAR, r, roundsF, roundsB)
    #print(VAR)

    if name == "qarmav1":
        omitFirstTweakAdd = False
        connectTweaks = True
        equalForwardAndBackwardTweaks = True
    elif name == "qarmav2":
        omitFirstTweakAdd = True
        connectTweaks = False
        equalForwardAndBackwardTweaks = False
    else:
        print("cipher name unknown!")
        stop

    startF = r + 1 - roundsF
    startB = r + 1 - roundsB
    minStart = min(startF,startB)

    s  = "\\iffalse\n\n"
    s += str(VAR).replace("'], '", "'],\n'")
    s += "\n\n\\fi\n\n"

    s += "\\begin{tikzpicture} \n"

    # difference between number of forward rounds in whole cipher and those that are in the characteristic

    # tweaks, correct

    for i in range(r+1):
        if not ((i == 0) and omitFirstTweakAdd):
            if (i == 0):
                xcoord = 1
            else:
                xcoord = 5 + 6 * (i-1)

            s += '\\node[state] at (' + str(xcoord) + ',0) (ft-' + str(i)  + ') {\\MatrixSingleState{\\arrayofnumbers{black}{' + VAR['ft'][i] + '}}};\n'

            if not equalForwardAndBackwardTweaks:
                s += '\\node[state] at (' + str(xcoord) + ',-6) (bt-' + str(i)  + ') {\\MatrixSingleState{\\arrayofnumbers{black}{' + VAR['bt'][i] + '}}};\n'

            s += '\\node[miniXOR]  at (' + str(xcoord)+ ',' + '-2' + ') (ftxor-' + str(i)+ ') {};\n'
            s += '\\node[miniXOR]  at (' + str(xcoord)+ ',' + '-4' + ') (btxor-' + str(i)+ ') {};\n'

    if connectTweaks:
        for i in range(r):
            s += '\\draw[cross line, arrow] (ft-' + str(i) + ') -- node[above] {\\scriptsize $h,\\omega$} (ft-' + str(i+1) + ');\n'
            if not equalForwardAndBackwardTweaks:
                s += '\\draw[cross line, arrow] (bt-' + str(i+1) + ') -- node[above] {\\scriptsize $\\bar h,\\bar\\omega$} (bt-' + str(i) + ');\n'

    # forward rounds
    # fat, (fpm,) fmc, fsc
    # with round zero containing only fat and round 1 omitting fmc

    for i in range(r+2):
        if i == 0:
            xcoord = 0
        elif i == 1:
            xcoord = 2
        else:
            xcoord = 6 * (i-1)

        if i == 0:
            s += '\\node[state] '
            s += 'at (' + str(xcoord)+ ',' +  '-2' + ') '
            s += '(fsc-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['fsc'][i] + '}}};\n'
        elif i == 1:
            s += '\\node[state] '
            s += 'at (' + str(xcoord)+ ',' +  '-2' + ') '
            s += '(fat-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['fat'][i] + '}}};\n'

            s += '\\node[state] '
            s += 'at (' + str(xcoord+2)+ ',' +  '-2' + ') '
            s += '(fsc-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['fsc'][i] + '}}};\n'
        else:
            s += '\\node[state] '
            s += 'at (' + str(xcoord)+ ',' +  '-2' + ') '
            s += '(fat-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['fat'][i] + '}}};\n'

            s += '\\node[state] '
            s += 'at (' + str(xcoord+2)+ ',' +  '-2' + ') '
            s += '(fmc-' + str(i) + ')'
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['fmc'][i] + '}}};\n'

            s += '\\node[state] '
            s += 'at (' + str(xcoord+4)+ ',' +  '-2' + ') '
            s += '(fsc-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['fsc'][i] + '}}};\n'

    # central rounds: there will be a single tau M tau arrow

    # backward rounds
    # bsc, bat, (bpm,) bmc

    for i in range(r+2):
        if i == 0:
            xcoord = 0
        elif i == 1:
            xcoord = 2
        else:
            xcoord = 6 * (i-1)

        if i == 0:
            s += '\\node[state] '
            s += 'at (' + str(xcoord)+ ',' +  '-4' + ') '
            s += '(bsc-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['bsc'][i] + '}}};\n'
        elif i == 1:
            s += '\\node[state] '
            s += 'at (' + str(xcoord)+ ',' +  '-4' + ') '
            s += '(bat-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['bat'][i] + '}}};\n'

            s += '\\node[state] '
            s += 'at (' + str(xcoord+2)+ ',' +  '-4' + ') '
            s += '(bsc-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['bsc'][i] + '}}};\n'
        else:
            s += '\\node[state] '
            s += 'at (' + str(xcoord)+ ',' +  '-4' + ') '
            s += '(bat-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['bat'][i] + '}}};\n'

            s += '\\node[state] '
            s += 'at (' + str(xcoord+2)+ ',' +  '-4' + ') '
            s += '(bmc-' + str(i) + ')'
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['bmc'][i] + '}}};\n'

            s += '\\node[state] '
            s += 'at (' + str(xcoord+4)+ ',' +  '-4' + ') '
            s += '(bsc-' + str(i) + ') '
            s += '{\\MatrixSingleState{\\arrayofnumbers{black}{'
            s += VAR['bsc'][i] + '}}};\n'

    # Decoration of start and end of CD. KRC

    s += '\\node[draw, thin, rounded corners=0.6mm, fit={(fsc-' + str(startF) + ')}, inner sep=0.6mm] (X) {};\n'
    if (startB > 0):
        s += '\\node[draw, thin, rounded corners=0.6mm, fit={(bsc-' + str(startB) + ')}, inner sep=0.6mm] (X) {};\n'

    s += '\\node[red, draw, thin, rounded corners=0.6mm, fit={(bsc-0)}, inner sep=0.6mm] (X) {};\n'
    s += '\\node[red, draw, thin, rounded corners=0.6mm, fit={(fsc-0)}, inner sep=0.6mm] (X) {};\n'

    # Connections and Arrow

    for i in range(1,r+2):
        if i == 1:
            if i > startF:
                if omitFirstTweakAdd:
                    s += '\\draw[cross line, arrow] (fsc-0) -- (fat-1);\n'
                    s += '\\draw[cross line, arrow] (fat-1)  -- node[above] {\\scriptsize $S$}  (fsc-1);\n'
                else:
                    s += '\\draw[cross line, arrow] (fsc-0) -- (ftxor-0);\n'
                    s += '\\draw[cross line, arrow] (ftxor-0) -- (fat-1);\n'
                    s += '\\draw[cross line, arrow] (fat-1)  -- node[above] {\\scriptsize $S$}  (fsc-1);\n'
            else:
                if omitFirstTweakAdd:
                    s += '\\draw[cross line, worra,red] (fsc-0)  -- (fat-1);\n'
                    s += '\\draw[cross line, worra,red] (fat-1)  -- node[above] {\\scriptsize $\\mybar S$}  (fsc-1);\n'
                else:
                    s += '\\draw[cross line, worra,red] (fsc-0) -- (ftxor-0);\n'
                    s += '\\draw[cross line, worra,red] (ftxor-0) -- (fat-1);\n'
                    s += '\\draw[cross line, worra,red] (fat-1)  -- node[above] {\\scriptsize $\\mybar S$}  (fsc-1);\n'

            if i > startB:
                if omitFirstTweakAdd:
                    s += '\\draw[cross line, worra] (bsc-0) --  (bat-1);\n'
                    s += '\\draw[cross line, worra] (bat-1)  -- node[above] {\\scriptsize $\\mybar S$}  (bsc-1);\n'
                else:
                    s += '\\draw[cross line, worra] (bsc-0) -- (btxor-0);\n'
                    s += '\\draw[cross line, worra] (btxor-0) -- (bat-1);\n'
                    s += '\\draw[cross line, worra] (bat-1)  -- node[above] {\\scriptsize $\\mybar S$}  (bsc-1);\n'
            else:
                if omitFirstTweakAdd:
                    s += '\\draw[cross line, worra,red] (bsc-0) -- (bat-1);\n'
                    s += '\\draw[cross line, worra,red] (bat-1)  -- node[above] {\\scriptsize $\\mybar S$}  (bsc-1);\n'
                else:
                    s += '\\draw[cross line, worra,red] (bsc-0) -- (btxor-0);\n'
                    s += '\\draw[cross line, worra,red] (btxor-0) -- (bat-1);\n'
                    s += '\\draw[cross line, worra,red] (bat-1)  -- node[above] {\\scriptsize $\\mybar S$}  (bsc-1);\n'
        else:
            if i > startF:
                s += '\\draw[cross line, arrow] (fsc-' + str(i-1) + ') -- (ftxor-' + str(i-1) + ');\n'
                s += '\\draw[cross line, arrow] (ftxor-' + str(i-1) + ') -- (fat-' + str(i) + ') ;\n'
                s += '\\draw[cross line, arrow] (fat-' + str(i) + ') -- node[above] {\\scriptsize $\\tau,M$} (fmc-' + str(i) + ');\n'
                s += '\\draw[cross line, arrow] (fmc-' + str(i) + ') -- node[above] {\\scriptsize $S$} (fsc-' + str(i) + ');\n'
            else:
                s += '\\draw[cross line, worra,red] (fsc-' + str(i-1) + ') -- (ftxor-' + str(i-1) + ');\n'
                s += '\\draw[cross line, worra,red] (ftxor-' + str(i-1) + ') -- (fat-' + str(i) + ') ;\n'
                s += '\\draw[cross line, worra,red] (fat-' + str(i) + ') -- node[above] {\\scriptsize $\\tau,M$} (fmc-' + str(i) + ');\n'
                s += '\\draw[cross line, worra,red] (fmc-' + str(i) + ') -- node[above] {\\scriptsize $S$} (fsc-' + str(i) + ');\n'

            if i > startB:
                s += '\\draw[cross line, worra] (bsc-' + str(i-1) + ') -- (btxor-' + str(i-1) + ');\n'
                s += '\\draw[cross line, worra] (btxor-' + str(i-1) + ') -- (bat-' + str(i) + ');\n'
                s += '\\draw[cross line, worra] (bat-' + str(i) + ') -- node[above] {\\scriptsize $\\mybar\\tau,M$} (bmc-' + str(i) + ');\n'
                s += '\\draw[cross line, worra] (bmc-' + str(i) + ') -- node[above] {\\scriptsize $\\mybar S$} (bsc-' + str(i) + ');\n'
            else:
                s += '\\draw[cross line, worra,red] (bsc-' + str(i-1) + ') -- (btxor-' + str(i-1) + ');\n'
                s += '\\draw[cross line, worra,red] (btxor-' + str(i-1) + ') -- (bat-' + str(i) + ');\n'
                s += '\\draw[cross line, worra,red] (bat-' + str(i) + ') -- node[above] {\\scriptsize $\\mybar\\tau,M$} (bmc-' + str(i) + ');\n'
                s += '\\draw[cross line, worra,red] (bmc-' + str(i) + ') -- node[above] {\\scriptsize $\\mybar S$} (bsc-' + str(i) + ');\n'

    for i in range(r+1):
        if not ((i == 0) and omitFirstTweakAdd):
            if equalForwardAndBackwardTweaks:
                s += '\\draw[cross line, connect] (ft-' + str(i) + ') -- ($(ft-' + str(i) + ')+(0,-0.8)$);\n'
                s += '\\draw[cross line, connect, dashed] ($(ft-' + str(i) + ')+(0,-0.8)$) -- ($(ft-' + str(i) + ')+(0,-1.5)$);\n'
                s += '\\draw[cross line, arrow] ($(ft-' + str(i) + ')+(0,-1.5)$) -- (ftxor-' + str(i)+ ');\n'
                s += '\\draw[cross line, connect, dashed] ($(btxor-' + str(i) + ')+(0,1.2)$) -- ($(btxor-' + str(i) + ')+(0,0.5)$);\n';
                s += '\\draw[cross line, arrow] ($(btxor-' + str(i) + ')+(0,0.5)$) -- (btxor-' + str(i) + ');\n'
            else:
                s += '\\draw[cross line, arrow] (ft-' + str(i) + ') -- (ftxor-' + str(i)+ ');\n'
                s += '\\draw[cross line, arrow] (bt-' + str(i) + ') -- (btxor-' + str(i)+ ');\n'

    s += '\\draw[cross line, arrow] (fsc-' + str(r+1) + ') -- node[right] {\\scriptsize $\\tau,M,\\mybar \\tau$} (bsc-' + str(r+1) + ');\n'


    # finalise

    s += "\\end{tikzpicture}\n"

    return s

if __name__ == '__main__':

    '''
    f = open("kr-distinguisher323-cb2.tex", "w")
    VAR = { 'fsc': ['0,0,0,0,0,0,0,E,5,0,0,0,0,0,0,0', '0,0,0,0,5,0,0,0,F,0,0,0,5,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'fat': ['B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'fpm': ['B,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'fmc': ['0,0,0,0,7,0,0,0,E,0,0,0,7,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'fwn': ['0,0,0,0,7,0,0,0,3,0,0,0,7,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'bsc': ['8,0,F,E,0,1,6,B,F,0,C,0,0,F,0,C', '8,0,0,0,0,0,0,E,5,0,0,0,0,0,0,0', '0,0,0,0,5,0,0,0,F,0,0,0,5,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'bat': ['8,0,F,0,0,1,0,0,F,0,C,0,0,F,0,C', '3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'bpm': ['8,0,0,F,C,0,0,0,1,0,0,F,C,0,0,F', '3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'bmc': ['4,0,0,0,0,0,0,F,2,0,0,0,0,0,0,0', '0,0,0,0,6,0,0,0,C,0,0,0,6,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'bwn': ['7,0,0,0,0,0,0,3,7,0,0,0,0,0,0,0', '0,0,0,0,3,0,0,0,3,0,0,0,3,0,0,0', '0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0'],
            'ft': ['0,0,6,B,0,0,0,0,0,0,0,0,0,0,0,D', '0,0,0,E,0,0,6,B,0,0,0,0,0,0,0,0', 'B,0,0,0,0,0,0,E,5,0,0,0,0,0,0,0', '0,0,0,0,5,0,0,0,F,0,0,0,5,0,0,0'],
            'bt': ['0,0,6,B,0,0,0,0,0,0,0,0,0,0,0,D', '0,0,0,E,0,0,6,B,0,0,0,0,0,0,0,0', 'B,0,0,0,0,0,0,E,5,0,0,0,0,0,0,0', '0,0,0,0,5,0,0,0,F,0,0,0,5,0,0,0']}

    s = createTikz("qarmav1", VAR, 3, 2, 3)
    print(s,file=f)
    f.close()
    '''

    '''
    f = open("kr-distinguisher212.tex", "w")
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
    s = createTikz("qarmav1", VAR12, 2, 1, 2)
    print(s,file=f)
    f.close()
    '''

    f = open("kr-distinguisher323.tex", "w")
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
    s = createTikz("qarmav1", VAR23, 3, 2, 3)
    print(s,file=f)
    f.close()
