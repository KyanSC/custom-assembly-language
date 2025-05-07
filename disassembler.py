import sys

op_codes = {
    "000000": "R",
    "001000": "addi",
    "000100": "beq",
    "000101": "bne",
    "000010": "jump",
    "011000": "threept",
    "011001": "CUSTOM",
    "011010": "replay",
    "011011": "buzzer"
}

func_codes = {
    "100000": "add",
    "100010": "sub",
    "101010": "slt",
    "011010": "div",
    "010000": "mfhi",
    "010010": "mflo",
    "000001": "dunk",
    "000010": "steal",
    "001000": "print",
    "000100": "boxout",
    "000101": "cross",
    "000110": "block",
    "000111": "rebound",
}

registers = {format(i, '05b'): f"r{i}" for i in range(16)}

def disassemble_file(filename):
    with open(filename, "r") as infile, open("disassembled.asm", "w") as outfile:
        for line in infile:
            line = line.strip()
            if line:
                asm = line  # Keep original line for debugging
                outfile.write(asm + "\n")

if __name__ == "__main__":
    program_number = sys.argv[1] if len(sys.argv) > 1 else "1"
    input_filename = "program_output.bin"
    disassemble_file(input_filename)
