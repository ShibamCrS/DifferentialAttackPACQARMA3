'''
Original version created on Apr 3, 2014

@author: XXXXXX
@author: XXXXXX
@author: XXXXXX
'''

from config import (PATH_STP, PATH_BOOLECTOR, PATH_CRYPTOMINISAT,
                    MAX_WEIGHT,MAX_CHARACTERISTICS)

from sys import stdout, stderr
import subprocess
import random
import math
import os
import time
import re
import sys
from createTikzKR import createTikz
from createTable import writeKRC
from cryptosmt import getFormat
import numbers
import shutil
import logging
from pathlib import Path

###############################################################################

import threading
import time
import click

def spinner(message="Processing"):
    def spin():
        spinner_chars = "|/-\\"
        i = 0
        while not done.is_set():
            click.echo(f"\r{message} {spinner_chars[i % len(spinner_chars)]}", nl=False)
            time.sleep(0.1)
            i += 1

    done = threading.Event()
    thread = threading.Thread(target=spin)
    thread.start()

    return done, thread

def stop_spinner(done, thread):
    done.set()
    thread.join()
    click.echo("\r", nl=False)  # Clear the spinner

###############################################################################

def latexIt(cipher, parameters, texFilename):

    parameter = parameters["parameter"]
    roundsF = parameters["roundsF"]
    roundsB = parameters["roundsB"]

    print(str(cipher.VAR).replace("'], '", "'],\n'"))
    tikzOutput = createTikz(cipher.name, cipher.VAR, parameter, roundsF, roundsB)

    prevwd = os.getcwd()
    os.chdir("./paper/")

    texFile = open(texFilename, 'w')
    tex_doc_start(texFile)
    texFile.write(tikzOutput)
    tex_doc_end(texFile)
    texFile.close()

    # stdout, stderr = subprocess.DEVNULL, subprocess.DEVNULL
    print(f"Start LaTeX on {texFilename}...")
    subprocess.check_call(['pdflatex', texFilename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("...Finished LaTeX")

    dirname = os.path.dirname(texFilename)
    basename = os.path.basename(texFilename)

    shutil.move(Path(texFilename).with_suffix('.tex'), Path("fig",texFilename).with_suffix('.tex'))
    shutil.move(Path(texFilename).with_suffix('.pdf'), Path("fig",texFilename).with_suffix('.pdf'))

    for suffix in ['.synctex.gz', '.aux', '.fls', '.log', '.out', '.fdb_latexmk']:
        try:
            os.remove(Path(basename).with_suffix(suffix))
        except:
            print("could not remove", str(Path(basename).with_suffix(suffix)))

    os.chdir(prevwd)


def findMinWeightCharacteristic(cipher, parameters):
    """
    Find a characteristic of minimal weight for the cipher
    parameters = [parameter, wordsize, sweight, isIterative, fixedVariables]
    """

    print("\n----------------------------------------------------------")
    print("Starting search for characteristic with minimal weight\n"
           "{}".format(parameters["config"]) )
    print("----------------------------------------------------------")

    start_time = time.time()

    while not reachedTimelimit(start_time, parameters["timelimit"]) and \
        parameters["sweight"] < parameters["endweight"]:

        filenameCommon = getFormat(parameters)
        solFilename    = f"tmp/{filenameCommon}.sol"
        yamlFilename   = f"examples/{filenameCommon}.yaml"
        texFilename    = f"{filenameCommon}.tex"
        tableFilename  = f"krcs/{filenameCommon}.txt"
        stpFile        = f"tmp/{filenameCommon}.stp"

        # Construct problem instance for given parameters
        variables = cipher.createSTP(stpFile, parameters)
        # print(variables)

        current_time = round(time.time() - start_time, 2)
        message = f"Search for weight = {parameters["sweight"]} started at {current_time}s ..."
        done, thread = spinner(message)
        result = solveSTP(stpFile)
        os.remove(stpFile)
        stop_spinner(done, thread)
        current_time = round(time.time() - start_time, 2)
        print(" : ended at {}s".format(current_time), flush=True)

        # Check if a characteristic was found
        if foundSolution(result):
            weight, characteristic = getCharSTPOutput(result)
            weight = int(parameters["sweight"])
            # cipher.printSol(parameters, characteristic, weight, solFilename, current_time)
            cipher.printDiffCFormat(parameters, characteristic, weight)
            cipher.createYaml(parameters, characteristic, weight, yamlFilename)
            print(str(yamlFilename))
            cipher.varToVal(parameters, characteristic)
            cipher.printInputPatCFormat(parameters, cipher.VAR)

            # print(f'{parameters["sweight"] = }')
            if parameters["writeKRC"]:
                writeKRC(parameters["sweight"], cipher.VAR, tableFilename)

            if parameters["latex"]:
                latexIt(cipher, parameters, texFilename)
                break
        else:
            print("nothing...")

        parameters["sweight"] += 1

    return parameters["sweight"]


def findAllCharacteristicRepresentatives(cipher, parameters):
    """
    Outputs all characteristics of a specific weight by excluding
    solutions iteratively. How to exclude characteristics is in a
    different function. This function is in general very slow and
    can generate a lot of data.
    """
    start_time = time.time()
    total_num_characteristics = 0

    while True:

        if (total_num_characteristics == 0):
            filenamesCommonRoot = getFormat(parameters)
            trailFile = f"tmp/trail_{filenamesCommonRoot}.sol"
            f = open(trailFile, 'w')
            f.close()
            print()
            print(" =================================== ")
            print(" ============ Weight",parameters["sweight"],"============")
            print(" =================================== ")
            print()

        filenameCommon = filenamesCommonRoot + "_N_" + str(total_num_characteristics)
        solFilename    = f"tmp/{filenameCommon}.sol"
        yamlFilename   = f"examples/{filenameCommon}.yaml"
        texFilename    = f"{filenameCommon}.tex"
        tableFilename  = f"krcs/{filenameCommon}.txt"
        stpFile        = f"tmp/{filenameCommon}.stp"

        # Automatically considers the excluded characteristics in to parameters["blockedCharacteristics"]
        variables = cipher.createSTP(stpFile, parameters)

        message = f"Search for weight = {parameters["sweight"]} started at {current_time}s ..."
        done, thread = spinner(message)
        result = solveSTP(stpFile)
        os.remove(stpFile)
        stop_spinner(done, thread)

        # Check for solution
        if foundSolution(result):
            f = open(trailFile, 'a')
            current_time = round(time.time() - start_time, 2)
            weight, characteristic = getCharSTPOutput(result)
            cipher.printDiff(parameters, characteristic, weight, f)
            f.close()

            # Add one differential to exclude to parameters["blockedCharacteristics"]
            # this eliminates a whole class of characteristics, but keeps the
            # characteristic of minimum weight for the differential.

            cipher.excludeDiff(parameters, characteristic)
            print("\tTime: {}s".format(round(time.time() - start_time, 2)))

            weight, characteristic = getCharSTPOutput(result)
            # cipher.printSol(parameters, characteristic, weight, solFilename, current_time)
            weight = int(parameters["sweight"])
            cipher.printDiffCFormat(parameters, characteristic, weight)
            cipher.createYaml(parameters, characteristic, weight, yamlFilename)
            print(str(yamlFilename))
            cipher.varToVal(parameters, characteristic)
            cipher.printInputPatCFormat(parameters, cipher.VAR)

            if parameters["writeKRC"]:
                writeKRC(parameters["sweight"], cipher.VAR, tableFilename)

            if parameters["latex"]:
                latexIt(cipher, parameters, texFilename)

            total_num_characteristics += 1

        else:
            current_time = round(time.time() - start_time, 2)
            print("Found {} characteristics with weight {}".format(
                total_num_characteristics, parameters["sweight"]))
            print("\tTime: {}s".format(round(time.time() - start_time, 2)))

            parameters["sweight"] += 1
            total_num_characteristics = 0

    return

debugComputeProbability = False

def computeProbabilityOfDifferentials(cipher, parameters):
    """
    Computes the probability of the differential by iteratively
    summing up all characteristics of a specific weight using
    a SAT solver.
    """

    rnd_string_tmp = '%030x' % random.randrange(16**30)

    if debugComputeProbability:
        sat_logfile = "tmp/satlog{}.tmp".format(rnd_string_tmp)

    diff_prob = 0
    characteristics_found = 0

    start_time = time.time()

    filenameCommon = format(parameters["fileFormat"])
    solFilename    = f"cluster_data/{filenameCommon}.sol"
    f = open(solFilename, "w")
    f.close()

    while not reachedTimelimit(start_time, parameters["timelimit"]) and \
        parameters["sweight"] < parameters["endweight"]:

        if debugComputeProbability:
            if os.path.isfile(sat_logfile):
                os.remove(sat_logfile)

        stp_file = "tmp/{}_{}_save.stp".format(cipher.name, rnd_string_tmp)
        cipher.createSTP(stp_file, parameters)

        # Start solver
        done, thread = spinner("")
        sat_process = startSATsolver(stp_file)
        if debugComputeProbability:
            log_file = open(sat_logfile, "w")

        # Find the number of solutions with the SAT solver
        print(f"Finding all trails of weight {parameters["sweight"]}")

        # Watch the process and count solutions
        solutions = 0
        print("--- Time: 0s, Solutions: 0  ", end="", flush=True)

        while sat_process.poll() is None:
            # print(sat_process.poll())
            line = sat_process.stdout.readline().decode("utf-8")
            if debugComputeProbability:
                log_file.write(line)
            if "s SATISFIABLE" in line:
                solutions += 1
                #print("*",end="", flush=True)
                if solutions % 100 == 0:
                    stop_spinner(done, thread)
                    ERASE_LINE = '\033[K'
                    print("\r" + ERASE_LINE,end="")
                    print("\r--- Time: {}s, Solutions: {}  ".format(round(time.time() - start_time, 2), solutions // 2), end="", flush=True)
                    done, thread = spinner("")

        if debugComputeProbability:
            log_file.close()

        stop_spinner(done, thread)
        ERASE_LINE = '\033[K'
        print("\r" + ERASE_LINE,end="")
        print("\r--- Time: {}s, Solutions: {}".format(round(time.time() - start_time, 2), solutions // 2), flush=True)

        if debugComputeProbability:
            assert solutions == countSolutionsLogfile(sat_logfile)

        # The encoded CNF contains every solution twice
        solutions //= 2

        # Print result
        diff_prob += math.pow(2, -parameters["sweight"]) * solutions
        characteristics_found += solutions
        if diff_prob > 0.0:
            #print("\tSolutions: {}".format(solutions))
            print("\tTrails found: {}".format(characteristics_found))
            print("\tCurrent Probability: " + str(math.log(diff_prob, 2)))
            print("\tTime: {}s".format(round(time.time() - start_time, 2)))
        f = open(solFilename, "a")
        f.write(str(parameters["sweight"]) + " -> "+ str(characteristics_found)+ "\n")
        f.close()
        parameters["sweight"] += 1

    if debugComputeProbability:
        os.remove(rnd_string_tmp)

    return diff_prob


def computeProbabilityOfTruncatedDifferentials(cipher, parameters):
    """
    Computes the probability of the truncated differential by iteratively
    summing up all characteristics of a specific truncated differential a
    SAT solver.
    """

    rnd_string_tmp = '%030x' % random.randrange(16**30)

    if debugComputeProbability:
        sat_logfile = "tmp/satlog{}.tmp".format(rnd_string_tmp)

    diff_prob = 0
    characteristics_found = 0

    start_time = time.time()

    while not reachedTimelimit(start_time, parameters["timelimit"]) and \
        int(parameters["sweight"]) < int(parameters["endweight"]):

        if debugComputeProbability:
            if os.path.isfile(sat_logfile):
                os.remove(sat_logfile)

        stp_file = "tmp/{}_{}_save.stp".format(cipher.name, rnd_string_tmp)
        cipher.createSTP(stp_file, parameters)

        # Start solver
        done, thread = spinner("")
        sat_process = startSATsolver(stp_file)

        if debugComputeProbability:
            log_file = open(sat_logfile, "w")

        # Find the number of solutions with the SAT solver
        print("Finding all trails of weight {}".format(parameters["sweight"]))

        # Watch the process and count solutions
        solutions = 0
        print("--- Time: 0s, Solutions: 0  ", end="", flush=True)

        while sat_process.poll() is None:
            line = sat_process.stdout.readline().decode("utf-8")
            if debugComputeProbability:
                log_file.write(line)
            if "s SATISFIABLE" in line:
                solutions += 1
                print("*",end="", flush=True)
                if solutions % 100 == 0:
                    ERASE_LINE = '\033[K'
                    print("\r" + ERASE_LINE,end="")
                    print("\r--- Time: {}s, Solutions: {}  ".format(round(time.time() - start_time, 2), solutions // 2), end="", flush=True)

        if debugComputeProbability:
            log_file.close()

        ERASE_LINE = '\033[K'
        print("\r" + ERASE_LINE,end="")
        print("\r--- Time: {}s, Solutions: {}".format(round(time.time() - start_time, 2), solutions // 2), flush=True)

        if debugComputeProbability:
            assert solutions == countSolutionsLogfile(sat_logfile)

        # The encoded CNF contains every solution twice
        solutions //= 2

        # Print result
        diff_prob += math.pow(2, -parameters["sweight"]) * solutions
        characteristics_found += solutions
        if diff_prob > 0.0:
            #print("\tSolutions: {}".format(solutions))
            print("\tTrails found: {}".format(characteristics_found))
            print("\tCurrent Probability: " + str(math.log(diff_prob, 2)))
            print("\tTime: {}s".format(round(time.time() - start_time, 2)))
        parameters["sweight"] += 1

    if debugComputeProbability:
        os.remove(rnd_string_tmp)

    return diff_prob


def findMinKeyWeightDifferential(cipher, parameters):
    """
    Find a differential of minimal weight for the key guess
    """

    print("----------------------------------------------------------")
    print("Starting search for differential with minimal key guess\n"
           "{}".format(parameters["config"]) )
    print("----------------------------------------------------------")

    start_time = time.time()

    while not reachedTimelimit(start_time, parameters["timelimit"]) and \
        parameters["sweight"] < parameters["endweight"]:

        # Construct problem instance for given parameters
        stpFile="tmp/{}.stp".format(parameters["fileFormat"])
        variables = cipher.createSTP(stpFile, parameters)

        # print(variables)
        result = solveSTP(stpFile)
        current_time = round(time.time() - start_time, 2)
        print("Weight: {} Time: {}s".format(parameters["sweight"], current_time))
        # Check if a characteristic was found
        if foundSolution(result):
            weight, characteristic = getCharSTPOutput(result)
            cipher.printSol(parameters, characteristic, weight, solFile, current_time)
            break

        parameters["sweight"] += 1

    return parameters["sweight"]


def getCharSTPOutput(output):
    """
    Parse the output of STP and construct a characteristic.
    """
    characteristic = {}
    weight = "0"

    for row in output.split('\n'):
        if re.match(r'ASSERT.*weight', row):
            try:
                weight = re.search(r'(?<=ASSERT\( weight = ).*(?= \);)', row).group(0)
            except:
                weight = "0";
        elif re.match(r'ASSERT\(.*\)', row):
            tmp = re.search(r'ASSERT\( ([a-z0-9A-Z]+) = ([a-z0-9A-Z]+)', row)
            var_name = tmp.group(1)
            var_value = tmp.group(2)
            characteristic[var_name] = var_value

    return weight, characteristic


def reachedTimelimit(start_time, timelimit):
    """
    Return True if the timelimit was reached.
    """
    if round(time.time() - start_time) >= timelimit and timelimit != -1:
        print("Reached the time limit of {} seconds".format(timelimit))
        return True
    return False


def countSolutionsLogfile(logfile_path):
    """
    Count the number of solutions in a CryptoMiniSat Logfile
    """
    with open(logfile_path, "r") as logfile:
        logged_solutions = 0
        for line in logfile:
            if "s SATISFIABLE" in line:
                logged_solutions += 1
        return logged_solutions
    return -1


def startSATsolver(stp_file):
    """
    Return CryptoMiniSat process started with the given stp_file.
    """
    # Start STP to construct CNF
    subprocess.check_output([PATH_STP, "--exit-after-CNF", "--output-CNF",
                             stp_file, "--CVC", "--disable-simplifications"])

    # Find the number of solutions with the SAT solver
    sat_params = [PATH_CRYPTOMINISAT,"--maxsol", str("10000000"),
                    "--verb", "0", "output_0.cnf"]

    sat_process = subprocess.Popen(sat_params, stderr=subprocess.PIPE,
                                   stdout=subprocess.PIPE)

    return sat_process


def solveSTP(stp_file, threads = 6):
    """
    Returns the solution for the given SMT problem using STP.
    """
    stp_parameters=[PATH_STP,stp_file,"--CVC","--cryptominisat","--threads",str(threads)]
    #stp_parameters=[PATH_STP,stp_file,"--CVC","--cryptominisat"]
    result = subprocess.check_output(stp_parameters)

    return result.decode("utf-8")


def foundSolution(solver_result):
    """
    Check if a solution was found.
    """
    return "Valid" not in solver_result and "unsat" not in solver_result


def tex_doc_start(f):
    print(r"""\documentclass[varwidth=false]{standalone}
\input includes/macros.tex
\input tikz-defs.tex
\usepackage{qarma}
\input includes/representation-macs.tex
\begin{document}
""", file=f)


def tex_doc_end(f):
    print(r"""
\end{document}
""", file=f)
