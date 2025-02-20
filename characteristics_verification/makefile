# Compiler and flags
CC = gcc
CFLAGS = -O3
LIB = -lm
# Source file
SRC = main.c

# Output directory for executables
BIN_DIR = bin

# List of defines (add more as needed)
DEFINES = \
    EQ9 \
    EQ10 \
    EQ11 EQ10_PRIME \
    EQ13 EQ13_STAR EQ13_PRIME EQ13_PRIME_STAR \
    EQ15 EQ15_STAR \
    EQ16 \
    EQ18 EQ18_PRIME \
    FIG12 FIG12_STAR \
    FIG13 FIG13_STAR \

# Targets for each define
TARGETS = $(addprefix $(BIN_DIR)/, $(DEFINES))

# Default target
all: $(TARGETS)

# Rule to compile each target
$(BIN_DIR)/%: $(SRC)
	mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) -D$* $< -o $@ $(LIB)

# Clean rule to remove executables and the bin directory
clean:
	rm -rf $(BIN_DIR)
