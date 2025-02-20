#!/usr/bin/env python3

import yaml
import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *

import search as search
# import usingApproxmc as usingApproxmc
from ciphers import (qarmav1, qarmav2)
from config import PATH_STP, PATH_CRYPTOMINISAT, PATH_BOOLECTOR, MAX_WEIGHT

from argparse import ArgumentParser, RawTextHelpFormatter
from argparse_backport import BooleanOptionalAction

batch = False

def batchsearch(tool_parameters, parameter, zc = 0):
    """
    Starts the search tool for the given parameters
    """

    cipher_suite = {"qarmav1" : qarmav1.QarmaCipher(),
                    "qarmav2" : qarmav2.QarmaCipher()}
    cipher = None

    if tool_parameters["cipher"] in cipher_suite:
        cipher = cipher_suite[tool_parameters["cipher"]]
    else:
        print("Cipher not supported!")
        return

    tool_parameters["parameter"] = parameter
    tool_parameters["roundsB"] = parameter
    tool_parameters["zerocells"] = zc
    for i in range(parameter, parameter+1):
        tool_parameters["roundsF"] = i
        tool_parameters["sweight"] = 0
        f = getFormat(tool_parameters)
        tool_parameters["fileFormat"] = f
        c = getConfig(tool_parameters)
        tool_parameters["config"] = c
        search.findMinWeightCharacteristic(cipher, tool_parameters)

    return


def startsearch(tool_parameters):
    """
    Starts the search tool for the given parameters
    """

    cipher_suite = {"qarmav1" : qarmav1.QarmaCipher(),
                    "qarmav2" : qarmav2.QarmaCipher()}
    cipher = None

    if tool_parameters["cipher"] in cipher_suite:
        cipher = cipher_suite[tool_parameters["cipher"]]
    else:
        print("Cipher not supported!")
        return

    # Handle program flow
    if tool_parameters["mode"] == 0:
        search.findMinWeightCharacteristic(cipher, tool_parameters)
    elif tool_parameters["mode"] == 1:
        search.computeProbabilityOfDifferentials(cipher, tool_parameters)
    elif tool_parameters["mode"] == 2:
        search.computeProbabilityOfTruncatedDifferentials(cipher, tool_parameters)
    elif tool_parameters["mode"] == 3:
        search.findAllCharacteristicRepresentatives(cipher, tool_parameters)

    return


def checkenviroment():
    """
    Basic checks if the enviroment is set up correctly
    """

    if not os.path.exists("./tmp/"):
        os.makedirs("./tmp/")
    if not os.path.exists("./krcs/"):
        os.makedirs("./krcs/")

    if not os.path.exists(PATH_STP):
        print("ERROR: Could not find STP binary, please check config.py")
        exit()

    if not os.path.exists(PATH_CRYPTOMINISAT):
        print("WARNING: Could not find CRYPTOMINISAT binary, please check "
              "config.py.")

    if not os.path.exists(PATH_BOOLECTOR):
        print("WARNING: Could not find BOOLECTOR binary, \"--boolector\" "
              "option not available.")

    return


def loadparameters(args):
    """
    Get parameters from the argument list and inputfile.
    """

    params = {"cipher" : "qarmav1",
              "roundsF" : 2,
              "roundsB" : 2,
              "parameter" : 3,
              "tweaks" : 1,
              "zerocells" : 0,
              "cellnumber" : -1, # -1 means no bound on cellweight at start of core characteristic
              "centercellnumber" : -1, # -1 means no bound on cellweight at center characteristic
              "frontconecellnumber" : -1, # -1 means no bound on cellweight at start of key recovery characteristic
              "forcecellsfront" : None,
              "forcecellsback" : None,
              "zerocellsfront" : None,
              "zerocellsback" : None,
              "backsegmentweight" : None,
              "backsegmentlength" : None,
              "custom" : None,
              "customfile" : None,
              "mode" : 0,
              "wordsize" : 4,
              "blocksize" : 64,
              "sweight" : 0,
              "endweight" : MAX_WEIGHT,
              "addrecovery" : False,
              "weightfunction" : 0,
              "iterative" : False,
              "boolector" : False,
              "dot" : None,
              "latex" : None,
              "writeKRC" : None,
              "nummessages" : 1,
              "timelimit" : -1,
              "fixedVariables" : {},
              "blockedCharacteristics" : [],
              "config":"",
              "fileFormat":""}

    # Check if there is an input file specified
    if args.inputfile:
        with open(args.inputfile[0], 'r') as input_file:
            doc = yaml.load(input_file, Loader=yaml.Loader)
            print(doc)
            params.update(doc)
            if "fixedVariables" in doc:
                fixed_vars = {}
                for variable in doc["fixedVariables"]:
                    fixed_vars = dict(list(fixed_vars.items()) +
                                      list(variable.items()))
                params["fixedVariables"] = fixed_vars

    # Override parameters if they are set on commandline
    if args.cipher:
        params["cipher"] = args.cipher[0]

    if args.roundsF:
        params["roundsF"] = args.roundsF[0]
    if args.roundsB:
        params["roundsB"] = args.roundsB[0]

    if args.parameter:
        params["parameter"] = args.parameter[0]

    if args.custom:
        params["custom"] = args.custom[0]

    if args.customfile:
        params["customfile"] = args.customfile[0]

    if args.zerocells:
        params["zerocells"] = args.zerocells[0]
    else:
        params["zerocells"] = 0


    def testLL(LL):
        if type(LL) != list:
            print("not a list")
            quit()
        for L in LL:
            if type(L) != list:
                print("not a list")
                quit()
            for i in L:
                try:
                    num = int(i)
                except:
                    print("not a number")
                    quit()
                if (num < 0) or (num > 15):
                    print(f"invalid number {num}")
                    quit()

    if args.forcecellsfront:
        LL = eval(args.forcecellsfront[0])
        testLL(LL)
        params["forcecellsfront"] = LL
    else:
        params["forcecellsfront"] = None

    if args.forcecellsback:
        LL = eval(args.forcecellsback[0])
        testLL(LL)
        params["forcecellsback"] = LL
    else:
        params["forcecellsback"] = None

    if args.zerocellsfront:
        LL = eval(args.zerocellsfront[0])
        testLL(LL)
        params["zerocellsfront"] = LL
    else:
        params["zerocellsfront"] = None

    if args.zerocellsback:
        LL = eval(args.zerocellsback[0])
        testLL(LL)
        params["zerocellsback"] = LL
    else:
        params["zerocellsback"] = None

    if args.backsegmentweight:
        params["backsegmentlength"] = args.backsegmentweight[0]
        params["backsegmentweight"] = args.backsegmentweight[1]
    else:
        params["backsegmentweight"] = None

    if args.tweaks:
        params["tweaks"] = args.tweaks[0]

    if args.wordsize:
        params["wordsize"] = args.wordsize[0]

    if args.blocksize:
        params["blocksize"] = args.blocksize[0]

    if args.sweight:
        params["sweight"] = args.sweight[0]

    if args.cellnumber:
        params["cellnumber"] = args.cellnumber[0]

    if args.centercellnumber:
        params["centercellnumber"] = args.centercellnumber[0]

    if args.frontconecellnumber:
        params["frontconecellnumber"] = args.frontconecellnumber[0]

    if args.endweight:
        params["endweight"] = args.endweight[0]

    if args.addrecovery:
        params["addrecovery"] = args.addrecovery

    if args.weightfunction:
        params["weightfunction"] = args.weightfunction[0]
    else:
        params["weightfunction"] = 0

    if args.mode:
        params["mode"] = args.mode[0]

    if args.timelimit:
        params["timelimit"] = args.timelimit[0]

    if args.iterative:
        params["iterative"] = args.iterative

    if args.boolector:
        params["boolector"] = args.boolector

    if args.latex:
        params["latex"] = args.latex
    if args.writeKRC:
        params["writeKRC"] = args.writeKRC

    params["fileFormat"] = getFormat(params)
    print(params["fileFormat"])

    params["config"] = getConfig(params)
    print(params["config"])

    return params


def getFormat(params):
    s = "{}_r_{}{}{}".format(params["cipher"],params["parameter"],params["roundsF"],params["roundsB"])
    s += "_t_{}".format(params["tweaks"])
    if params["cellnumber"] != -1:
        s += "_cb_{}".format(params["cellnumber"])
    if params["centercellnumber"] != -1:
        s += "_ccb_{}".format(params["centercellnumber"])
    if params["frontconecellnumber"] != -1:
        s += "_fcb_{}".format(params["frontconecellnumber"])
    if params["addrecovery"]:
        s += "_KR"
    s += "_wf_{}".format(params["weightfunction"])
    if params["zerocells"]:
        s += "_zc_{}".format(params["zerocells"])
    if params["zerocellsfront"]:
        s += "_zcf_{}".format(params["zerocellsfront"]).replace(',','+').replace(" ",'').replace("[",'<').replace("]",'>')
    if params["zerocellsback"]:
        s += "_zcb_{}".format(params["zerocellsback"]).replace(',','+').replace(" ",'').replace("[",'<').replace("]",'>')
    if params["forcecellsfront"]:
        s += "_fcf_{}".format(params["forcecellsfront"]).replace(',','+').replace(" ",'').replace("[",'<').replace("]",'>')
    if params["forcecellsback"]:
        s += "_fcb_{}".format(params["forcecellsback"]).replace(',','+').replace(" ",'').replace("[",'<').replace("]",'>')
    s += "_W_{}".format(params["sweight"])
    return s

def getConfig(params):
    s = "{}: parameter {} roundsF {} roundsB {}".\
                        format(params["cipher"],\
                        params["parameter"],\
                        params["roundsF"],\
                        params["roundsB"])

    s += " tweaks {}".format(params["tweaks"])

    if params["cellnumber"] != -1:
        s += " cellnumber {}".format(params["cellnumber"])
    if params["centercellnumber"] != -1:
        s += " centercellnumber {}".format(params["centercellnumber"])
    if params["frontconecellnumber"] != -1:
        s += " frontconecellnumber {}".format(params["frontconecellnumber"])

    if params["addrecovery"]:
        s += " keyrecovery "
        s += " with zerocells = {}".format(params["zerocells"])
    s += " weight function {}".format(params["weightfunction"])

    return s

def main():
    """
    Parse the arguments and start the request functionality with the provided
    parameters.
    """
    parser = ArgumentParser(description="This tool finds the best differential"
                                        "trail in a cryptopgrahic primitive"
                                        "using STP and CryptoMiniSat.",
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument('--cipher', nargs=1, help="Options: simon, speck, ...")
    parser.add_argument('-s','--sweight', nargs=1, type=int,
                        help="Starting weight for the trail search.")
    parser.add_argument('--endweight', nargs=1, type=int,
                        help="Stop search after reaching endweight.")
    parser.add_argument('-r','--parameter', nargs=1, type=int,
                        help="The cipher parameter r, where the total rounds are 2r+2)")
    parser.add_argument('-F','--roundsF', nargs=1, type=int,
                        help="The forward number of rounds for the distinguisher, between 1 and parameter+1, extremes included")
    parser.add_argument('-B','--roundsB', nargs=1, type=int,
                        help="The backward number of rounds for the distinguisher, between 1 and parameter+1, extremes included")
    parser.add_argument('-w', '--wordsize', nargs=1, type=int,
                        help="Wordsize used for the cipher.")
    parser.add_argument('--blocksize', nargs=1, type=int,
                        help="Blocksize used for the cipher.")

    parser.add_argument('-z','--zerocells', nargs=1, type=int, default=0,
                        help="The number of zero cells at the beginning of the key-recovery differential")
    parser.add_argument('--zerocellsfront', '--zcf', nargs=1, type=str,
                        help='parameter is a list LL of lists L of cells for which there shold be at least one INACTIVE cell per L'
                        ' - at the beginning of the key-recovery characteristic, for each list L.', required=False)
    parser.add_argument('--zerocellsback', '--zcb', nargs=1, type=str,
                        help='parameter is a list LL of lists L of cells for which there shold be at least one INACTIVE cell per L'
                        ' - at the end of the key-recovery characteristic, for each list L.', required=False)
    parser.add_argument('--forcecellsfront', '--fcf', nargs=1, type=str,
                        help='parameter is a list LL of lists L of cells for which there shold be at least one ACTIVE cell per L'
                        ' - at the beginning of the key-recovery characteristic, for each list L.', required=False)
    parser.add_argument('--forcecellsback', '--fcb', nargs=1, type=str,
                        help='parameter is a list LL of lists L of cells for which there shold be at least one ACTIVE cell per L'
                        ' - at the end of the key-recovery characteristic, for each list L.', required=False)
    parser.add_argument('-c','--cellnumber', nargs=1, type=int,
                        help="Exact number of active cells at the beginning of the data path of the core characteristic")
    parser.add_argument('--centercellnumber', '--cc',nargs=1, type=int,
                        help="Exact number of active cells at the center of the data path")
    parser.add_argument('--frontconecellnumber', '--fcc', nargs=1, type=int,
                        help="Exact number of active cells at the beginning of the data path of the key recovery characteristic")

    parser.add_argument('--backsegmentweight', '--bsw', nargs=2, type=int, metavar=('WEIGHT','LENGTH'),
                        help="Exact number of active cells at the in the first a cells of the back")

    parser.add_argument('--custom', nargs=1, type=str,
                        help='custom commands')

    parser.add_argument('--customfile', nargs=1, type=str,
                        help='custom command in a file')

    parser.add_argument('-t','--tweaks', nargs=1, type=int,
                        help="The number of tweaks for the cipher")

    parser.add_argument('-k', '--addrecovery', default=False, action=BooleanOptionalAction,
                        help="Extends the characteristic to cover the whole cipher")

    parser.add_argument('-f', '--weightfunction', nargs=1, type=int, choices=[0, 1], default=0,
                        help="Selects the weight function: 0 is p, 1 is p+din. The latter can only be used with -k")

    parser.add_argument('--mode', nargs=1, type=int,
                        choices=[0, 1, 2, 3, 4], help=
                        "0 = search characteristic for fixed round\n"
                        "1 = compute clustered probability with fixed start differences and truncated end described in yaml file\n"  # computeProbabilityOfDifferentials
                        "2 = compute probability of truncated differentials\n"
                        "3 = like 0 but find characteristics that are representatives of unique starting states\n")

    parser.add_argument('--timelimit', nargs=1, type=int,
                        help="Set a timelimit for the search in seconds.")

    parser.add_argument('--iterative', action="store_true",
                        help="Only search for iterative characteristics")

    parser.add_argument('--boolector', action="store_true",
                        help="Use boolector to find solutions")

    parser.add_argument('--inputfile', nargs=1, help="Use an yaml input file to"
                                                     "read the parameters.")
    parser.add_argument('--latex', default=False, action=BooleanOptionalAction,
                        help="Print the trail in .tex format.")

    parser.add_argument('--writeKRC', default=False, action=BooleanOptionalAction,
                        help="Save the KRC? be careful, it may replace previous saved results")

    # Parse command line arguments and construct parameter list.
    args = parser.parse_args()
    params = loadparameters(args)

    # Check if enviroment is setup correctly.
    checkenviroment()

    # Start the solver
    if batch:
        batchsearch(params, 2, 0)
    else:
        startsearch(params)

if __name__ == '__main__':
    main()
