#import os
#myself = os.environ['USER']

import subprocess

# Paths to the STP and cryptominisat executable

try:
    rawout = subprocess.run(["brew", "--prefix"],capture_output=True).stdout
    base = rawout.decode()[:-1]
    PATH_STP = f'{base}/bin/stp'
    PATH_CRYPTOMINISAT = f'{base}/bin/cryptominisat5'
    PATH_BOOLECTOR = f'{base}/bin/boolector'
    
except FileNotFoundError:
    PATH_STP = "/usr/local/bin/stp"
    PATH_CRYPTOMINISAT = "/usr/local/bin/cryptominisat5"
    PATH_BOOLECTOR = "../boolector/build/bin/boolector"

# Maximum weight for characteristics to search for
MAX_WEIGHT = 200
# Maximum number of characteristics to search for a differential
MAX_CHARACTERISTICS = 10000000

#for mac
# PATH_STP = "/usr/local/bin/stp"
# PATH_CRYPTOMINISAT = "/usr/local/bin/cryptominisat5"
