op_codes = {
    "add": "000000",
    "sub": "000000",
    "slt": "000000",
    "beq": "000100",
    "bne": "000101",
    "jump": "000010",
    "div": "000000",
    "mfhi": "000000",
    "mflo": "000000",
    "addi": "001000",
    "threept": "011000",
    "dunk": "011001",
    "steal": "011001",
    "print": "011001",
    "boxout": "011001",
    "cross": "011001",
    "replay": "011010",
    "block": "011001",
    "rebound": "011001",
    "buzzer": "011011",
}

func_codes = {
    "add": "100000",
    "sub": "100010",
    "slt": "101010",
    "div": "011010",
    "mfhi": "010000",
    "mflo": "010010",
    "dunk": "000001",
    "steal": "000010",
    "print": "001000",
    "boxout": "000100",
    "cross": "000101",
    "block": "000110",
    "rebound": "000111",
}

registers = {f"r{i}": format(i, '05b') for i in range(16)}

def assemble(line):
    parts = line.strip().split()
    if not parts or line.startswith("#"):
        return ""
    instr = parts[0]
    if instr in func_codes:
        ops = [p.replace(",", "") for p in parts[1:]]
        rs = registers.get(ops[0], "00000")
        rt = registers.get(ops[1], "00000") if len(ops) > 1 else "00000"
        rd = registers.get(ops[2], "00000") if len(ops) > 2 else "00000"
        return op_codes[instr] + rs + rt + rd + "00000" + func_codes[instr]
    elif instr in ["addi", "beq", "bne", "threept"]:
        rt, rs, imm = parts[1].replace(",", ""), parts[2].replace(",", ""), parts[3]
        imm_bin = format(int(imm), '016b')
        return op_codes[instr] + registers[rs] + registers[rt] + imm_bin
    elif instr in ["print", "mfhi", "mflo"]:
        rt = parts[1].replace(",", "")
        return op_codes[instr] + "00000" + "00000" + registers[rt] + "00000" + func_codes[instr]
    elif instr == "jump":
        addr = format(int(parts[1]), '026b')
        return op_codes[instr] + addr
    elif instr == "replay":
        _, n = parts[1].replace(",", ""), parts[2]
        imm_bin = format(int(n), '016b')
        return op_codes[instr] + "00000" + "00000" + imm_bin
    elif instr == "buzzer":
        return op_codes[instr] + "0" * 26
    return ""

def interpret_file(filename):
    with open(filename, "r") as infile, open("program_output.bin", "w") as outfile:
        for line in infile:
            binary = assemble(line)
            if binary:
                outfile.write(binary + "\n")

if __name__ == "__main__":
    interpret_file("output_basketball.asm")
