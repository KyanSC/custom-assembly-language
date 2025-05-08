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

def disassemble_line(line):
    # Ensure the line is exactly 32 bits
    if len(line) != 32:
        return f"invalid instruction length: {len(line)}"
    
    opcode = line[0:6]
    
    # R-Type Instructions (e.g., add, sub, steal)
    if opcode == "000000" or opcode == "011001":  # R-type or custom
        rs = line[6:11]
        rt = line[11:16]
        rd = line[16:21]
        shamt = line[21:26]
        func = line[26:32]
        
        instr = func_codes.get(func, "unknown")
        if instr in ["steal", "print", "dunk", "boxout", "cross", "block", "rebound"]:  # Custom instructions with 2 registers
            return f"{instr} {registers[rs]}, {registers[rt]}"
        return f"{instr} {registers[rd]}, {registers[rs]}, {registers[rt]}"
    
    # I-Type Instructions (e.g., addi, beq, bne)
    elif opcode in ["001000", "000100", "000101"]:  # addi, beq, bne
        rs = line[6:11]
        rt = line[11:16]
        imm = line[16:32]
        instr = op_codes.get(opcode, "unknown")
        imm_value = int(imm, 2) if imm[0] == '0' else -((1 << 16) - int(imm, 2))  # Handle signed imm
        return f"{instr} {registers[rt]}, {registers[rs]}, {imm_value}"
    
    # J-Type Instruction (e.g., jump)
    elif opcode == "000010":  # Jump
        address = int(line[6:32], 2)
        return f"jump {address}"
    
    # Special Single Instructions (e.g., buzzer)
    elif opcode == "011011":
        return "buzzer"
    
    # Custom Loop Instruction (e.g., replay)
    elif opcode == "011010":  # replay
        rs = line[6:11]
        rt = line[11:16]
        imm = line[16:32]
        return f"replay {registers[rs]}, {int(imm, 2)}"
    
    return f"unknown {line}"

def disassemble_file(filename):
    with open(filename, "r") as infile, open("disassembled.asm", "w") as outfile:
        for line in infile:
            line = line.strip()
            if line:
                asm = disassemble_line(line)
                outfile.write(asm + "\n")

if __name__ == "__main__":
    program_number = sys.argv[1] if len(sys.argv) > 1 else "1"
    input_filename = "program_output.bin"
    disassemble_file(input_filename)
