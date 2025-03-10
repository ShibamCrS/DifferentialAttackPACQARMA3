'''
Created on Mar 28, 2014

Provides functions for constructing the input file for STP.
@author: XXXXXX
@author: XXXXXX
@author: XXXXXX
'''

import itertools

def blockCharacteristic(stpfile, characteristic, wordsize):
    """
    Excludes this characteristic from being found.
    """
    # print(characteristic)
    blockingStatement = "ASSERT(NOT("

    for key, value in characteristic.items():
        blockingStatement += "BVXOR({}, {}) | ".format(key, value)

    blockingStatement = blockingStatement[:-2]
    blockingStatement += ") = 0hex{});".format("0"*(wordsize // 4))
    stpfile.write(blockingStatement)
    return


def setupQuery(stpfile):
    """
    Adds the query and printing of counterexample to the stp stpfile.
    """
    stpfile.write("QUERY(FALSE);\n")
    stpfile.write("COUNTEREXAMPLE;\n")
    return


def setupVariables(stpfile, variables, wordsize):
    """
    Adds a list of variables to the stp stpfile.
    """
    stpfile.write(getStringForVariables(variables, wordsize) + '\n')
    return


def assertVariableValue(stpfile, a, b):
    """
    Adds an assert that a = b to the stp stpfile.
    """
    stpfile.write("ASSERT({} = {});\n".format(a, b))
    return


def getStringForVariables(variables, wordsize):
    """
    Takes as input the variable name, number of variables and the wordsize
    and constructs for instance a string of the form:
    x00, x01, ..., x30: BITVECTOR(wordsize);
    """
    command = ""
    for var in variables:
        command += var + ","

    command = command[:-1]
    command += ": BITVECTOR({0});".format(wordsize)
    return command


def assertNonZero(stpfile, variables, wordsize):
    stpfile.write(getStringForNonZero(variables, wordsize) + '\n')
    return


def getStringForNonZero(variables, wordsize):
    """
    Asserts that no all-zero characteristic is allowed
    """
    command = "ASSERT(NOT(("
    for var in variables:
        command += var + "|"

    command = command[:-1]
    command += ") = 0bin{}));".format("0" * wordsize)
    return command


def assertAZero(stpfile, variables, wordsize):
    stpfile.write(getStringForAZero(variables, wordsize) + '\n')
    return


def getStringForAZero(variables, wordsize):
    """
    Asserts that the zero characteristic contains a zero
    """
    command = "ASSERT(("
    for var in variables:
        command += var + "&"

    command = command[:-1]
    command += ") = 0bin{});".format("0" * wordsize)
    return command


def assertNonOne(stpfile, variables, wordsize):
    stpfile.write(getStringForNonOne(variables, wordsize) + '\n')
    return


def getStringForNonOne(variables, wordsize):
    """
    Asserts that no all-zero characteristic is allowed
    """
    command = "ASSERT(NOT(("
    for var in variables:
        command += var + "|"

    command = command[:-1]
    command += ") = 0bin{}));".format("1" * wordsize)
    return command


def limitWeight(stpfile, weight, p, wordsize, ignoreMSBs=0):
    """
    Adds the weight computation and assertion to the stp stpfile.
    """
    stpfile.write("limitWeight: BITVECTOR(16);\n")
    stpfile.write(getWeightString(p, wordsize, ignoreMSBs, "limitWeight") + "\n")
    stpfile.write("ASSERT(BVLE(limitWeight, {0:#018b}));\n".format(weight))
    return

# zzz to be done 9I forgot what)
def setupWeightComputationSum(stpfile, weight, p, wordsize, ignoreMSBs=0, weightVariable="weight"):
    """
    Assert that weight is equal to the sum of p.
    """
    stpfile.write("{}: BITVECTOR(16);\n".format(weightVariable))
    round_sum = ""
    for w in p:
        round_sum += w + ","
    if len(p) > 1:
        stpfile.write("ASSERT({} = BVPLUS({},{}));\n".format(weightVariable, 16, round_sum[:-1]))
    else:
        stpfile.write("ASSERT({} = {});\n".format(weightVariable, round_sum[:-1]))
    stpfile.write("ASSERT({0} = {1:#018b});\n".format(weightVariable,weight))
    return

def setupWeightComputation(stpfile, weight, p, wordsize, ignoreMSBs=0, weightVariable="weight", vectorLength=16):
    """
    Assert that weight is equal to the sum of the hamming weight of p.
    """
    stpfile.write("{}: BITVECTOR({});\n".format(weightVariable,vectorLength))
    stpfile.write(getWeightString(p, wordsize, ignoreMSBs, weightVariable) + "\n")
    if (weight != -1):
        stpfile.write("ASSERT({0} = {1:#018b});\n".format(weightVariable,weight))
    return

def setupWeightComputationCell(stpfile, weight, p, wordsize,weightVariable="cellbound"):
    """
    Assert that weight is equal to the sum of the or of the bits in p.
    """
    stpfile.write(getOrWeightString(p, wordsize,weightVariable) + "\n")
    stpfile.write("ASSERT({0} = {1:#07b});\n".format(weightVariable,weight))
    return

def getOrWeightString(variables, wordsize, weightVariable="cellbound"):
    """
    Asserts that the weight is equal to the or of bits of the
    given variables.
    """
    command = "ASSERT({} = BVPLUS(5,".format(weightVariable)
    for var in variables:
        tmp = "0b0000@("
        for bit in range(wordsize):
            tmp += "{0}[{1}:{1}]|".format(var, bit)
        command += tmp[:-1] + "),"
    if len(variables):
        command += "0bin00000,"
    command = command[:-1]
    command += "));"

    #print(command)
    return command

def getWordOr(word, wordsize):
    """
    Create expression of the LOGICAl OR of all bits in word of size wordsize bits
    """
    expression = ""
    for bit in range(wordsize):
        expression += "{0}[{1}:{1}]|".format(word,bit)
    expression = expression[:-1]

    return expression

def getWordOrForAllState(ORs, words, wordsize):
    """
    Create expressions of the LOGICAl OR of all bits in each word (cell) of a list of words(state)
    """
    command = ""
    for index in range(len(words)):
        command += "ASSERT({0} = {1});\n".format(ORs[index],getWordOr(words[index], wordsize))

    return command

def getWeightString(variables, wordsize, ignoreMSBs=0, weightVariable="weight"):
    """
    Asserts that the weight is equal to the hamming weight of the
    given variables.
    """
    # if len(variables) == 1:
    #     return "ASSERT({} = {});\n".format(weightVariable, variables[0])

    command = "ASSERT(({} = BVPLUS(16,".format(weightVariable)
    for var in variables:
        tmp = "0b00000000@(BVPLUS(8, "
        for bit in range(wordsize - ignoreMSBs):
            # Ignore MSBs if they do not contribute to
            # probability of the characteristic.
            tmp += "0bin0000000@({0}[{1}:{1}]),".format(var, bit)
        # Pad the constraint if necessary
        if (wordsize - ignoreMSBs) == 1:
            tmp += "0bin0,"
        command += tmp[:-1] + ")),"
    if len(variables):
        command += "0bin0000000000000000,"
    command = command[:-1]
    command += ")));"

    return command


def getStringEq(a, b, c):
    command = "(BVXOR(~{0}, {1}) & BVXOR(~{0}, {2}))".format(a, b, c)
    return command


def getStringAdd(a, b, c, wordsize):
    command = "(((BVXOR((~{0} << 1)[{3}:0], ({1} << 1)[{3}:0])".format(
        a, b, c, wordsize - 1)
    command += "& BVXOR((~{0} << 1)[{3}:0], ({2} << 1)[{3}:0]))".format(
        a, b, c, wordsize - 1)
    command += " & BVXOR({0}, BVXOR({1}, BVXOR({2}, ({1} << 1)[{3}:0]))))".format(
        a, b, c, wordsize - 1)
    command += " = 0bin{})".format("0" * wordsize)
    return command

def getStringForAndDifferential(a, b, c):
    """
    AND = valid(x,y,out) = (x and out) or (y and out) or (not out)
    """
    command = "(({0} & {2}) | ({1} & {2}) | (~{2}))".format(a, b, c)
    return command


def getStringLeftRotate(value, rotation, wordsize):
    if rotation % wordsize == 0:
        return "{0}".format(value)
    command = "((({0} << {1})[{2}:0]) | (({0} >> {3})[{2}:0]))".format(
        value, (rotation % wordsize), wordsize - 1, (wordsize - rotation) % wordsize)

    return command

def getStringRightRotate(value, rotation, wordsize):
    if rotation % wordsize == 0:
        return "{0}".format(value)
    command = "((({0} >> {1})[{2}:0]) | (({0} << {3})[{2}:0]))".format(
        value, (rotation % wordsize), wordsize - 1, (wordsize - rotation) % wordsize)
    return command

def add4bitSboxNibbles(sbox, x, y, w):
    variables = ["{0}[{1}:{1}]".format(x, 3),
                 "{0}[{1}:{1}]".format(x, 2),
                 "{0}[{1}:{1}]".format(x, 1),
                 "{0}[{1}:{1}]".format(x, 0),

                 "{0}[{1}:{1}]".format(y, 3),
                 "{0}[{1}:{1}]".format(y, 2),
                 "{0}[{1}:{1}]".format(y, 1),
                 "{0}[{1}:{1}]".format(y, 0),

                 "{0}[{1}:{1}]".format(w, 3),
                 "{0}[{1}:{1}]".format(w, 2),
                 "{0}[{1}:{1}]".format(w, 1),
                 "{0}[{1}:{1}]".format(w, 0)]
    command = add4bitSbox(sbox, variables)
    return command

def boundVariable(stpfile, words, bits, wordsize):
    for index in range(16):
        word = words[index]
        bit  = bits[index]
        for i in range(wordsize):
            stpfile.write("ASSERT(BVLE({0}[{1}:{1}],{2}[0:0]));\n".format(word,i,bit))

def add4bitSbox(sbox, variables):
    """
    Adds the constraints for the S-box and the weight
    for the differential transition.

    sbox is a list representing the S-box.

    variables should be a list containing the input and
    output variables of the S-box and the weight variables.

    S(x) = y

    The probability of the transitions is
    2^-{hw(w0||w1||w2||w3)}

    w ... hamming weight from the DDT table
    """
    assert(len(sbox) == 16)
    assert(len(variables) == 12)

    # First compute the DDT
    DDT = [[0]*16 for i in range(16)]

    for a in range(16):
        for b in range(16):
            DDT[a ^ b][sbox[a] ^ sbox[b]] += 1

    # Construct DNF of all valid trails
    trails = []

    # All zero trail with probability 1
    for input_diff in range(16):
        for output_diff in range(16):
            if DDT[input_diff][output_diff] != 0:
                tmp = []
                tmp.append((input_diff >> 3) & 1)
                tmp.append((input_diff >> 2) & 1)
                tmp.append((input_diff >> 1) & 1)
                tmp.append((input_diff >> 0) & 1)
                tmp.append((output_diff >> 3) & 1)
                tmp.append((output_diff >> 2) & 1)
                tmp.append((output_diff >> 1) & 1)
                tmp.append((output_diff >> 0) & 1)
                if DDT[input_diff][output_diff] == 2:
                    tmp += [0, 1, 1, 1] # 2^-3
                elif DDT[input_diff][output_diff] == 4:
                    tmp += [0, 0, 1, 1] # 2^-2
                elif DDT[input_diff][output_diff] == 8:
                    tmp += [0, 0, 0, 1] # 2^-1
                elif DDT[input_diff][output_diff] == 16:
                    tmp += [0, 0, 0, 0]
                trails.append(tmp)

    # Build CNF from invalid trails
    cnf = ""
    for prod in itertools.product([0, 1], repeat=len(trails[0])):
        # Trail is not valid
        if list(prod) not in trails:
            expr = ["~" if x == 1 else "" for x in list(prod)]
            clause = ""
            for literal in range(12):
                clause += "{0}{1} | ".format(expr[literal], variables[literal])

            cnf += "({}) &".format(clause[:-2])

    return "ASSERT({} = 0bin1);\n".format(cnf[:-2])
