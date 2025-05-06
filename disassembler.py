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

def disassemble_line(line):
    opcode = line[0:6]
    if opcode == "000000" or opcode == "011001":
        rs, rt, rd, shamt, func = line[6:11], line[11:16], line[16:21], line[21:26], line[26:]
        return f"{func_codes[func]} {registers[rd]}, {registers[rs]}, {registers[rt]}"
    elif opcode == "000010":
        addr = int(line[6:], 2)
        return f"jump {addr}"
    elif opcode == "011011":
        return "buzzer"
    else:
        rs, rt, imm = line[6:11], line[11:16], line[16:]
        instr = op_codes.get(opcode, "unknown")
        return f"{instr} {registers[rt]}, {registers[rs]}, {int(imm, 2)}"

def disassemble_file(filename):
    with open(filename, "r") as infile, open("disassembled.asm", "w") as outfile:
        for line in infile:
            line = line.strip()
            if line:
                asm = disassemble_line(line)
                outfile.write(asm + "\n")


if __name__ == "__main__":
    disassemble_file("program_output.bin")
