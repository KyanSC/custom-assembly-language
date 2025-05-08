import sys

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
    "bgtz": "000111",  # Added for loop conditions
    "la": "001111",    # Load address pseudo-instruction
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

def parse_immediate(imm_str):
    try:
        # Handle negative numbers
        if imm_str.startswith('-'):
            value = -int(imm_str[1:])
            # Convert to 16-bit two's complement
            if value < 0:
                value = (1 << 16) + value
            return format(value & 0xFFFF, '016b')
        else:
            value = int(imm_str)
            return format(value & 0xFFFF, '016b')
    except ValueError:
        # For string literals or labels, just return zeros
        return "0" * 16

def assemble(line):
    parts = line.strip().split()
    if not parts or line.startswith("#"):
        return ""
    
    # Handle labels
    if line.endswith(":"):
        return ""
    
    # Handle data segment directives
    if line.startswith("."):
        return ""
    
    instr = parts[0]
    if instr in op_codes:
        ops = [p.replace(",", "") for p in parts[1:]]
        
        # R-type instructions
        if op_codes[instr] == "000000" or op_codes[instr] == "011001":
            if len(ops) == 2:  # Two register format (e.g., steal, print)
                rs = registers.get(ops[0], "00000")
                rt = registers.get(ops[1], "00000")
                return op_codes[instr] + rs + rt + "00000" + "00000" + func_codes[instr]
            elif len(ops) == 3:  # Three register format (e.g., add, sub)
                rd = registers.get(ops[0], "00000")
                rs = registers.get(ops[1], "00000")
                rt = registers.get(ops[2], "00000")
                return op_codes[instr] + rs + rt + rd + "00000" + func_codes[instr]
            else:
                return ""
        
        # I-type instructions
        elif instr in ["addi", "beq", "bne", "bgtz", "la"]:
            if len(ops) < 2:
                return ""
            
            if instr == "addi":
                rt = registers.get(ops[0], "00000")
                rs = registers.get(ops[1], "00000")
                imm = parse_immediate(ops[2] if len(ops) > 2 else "0")
                return op_codes[instr] + rs + rt + imm
            elif instr == "bgtz":
                rs = registers.get(ops[0], "00000")
                imm = parse_immediate(ops[1] if len(ops) > 1 else "0")
                return op_codes[instr] + rs + "00000" + imm
            elif instr == "la":  # Load address pseudo-instruction
                rt = registers.get(ops[0], "00000")
                # For now, just use zeros for the address (will be filled in by linker)
                return op_codes[instr] + "00000" + rt + "0000000000000000"
            else:  # beq, bne
                rs = registers.get(ops[0], "00000")
                rt = registers.get(ops[1], "00000")
                imm = parse_immediate(ops[2] if len(ops) > 2 else "0")
                return op_codes[instr] + rs + rt + imm
        
        # J-type instructions
        elif instr == "jump":
            if len(ops) < 1:
                return ""
            target = ops[0]
            # For now, just use zeros for jump target (will be filled in by linker)
            return op_codes[instr] + "00000000000000000000000000"
        
        # Special instructions
        elif instr == "buzzer":
            return op_codes[instr] + "00000000000000000000000000"
    
    return ""

def interpret_file(filename):
    # First pass: collect label addresses and string data
    current_addr = 0
    labels = {}
    data_segment = []
    in_data_segment = False
    
    with open(filename, "r") as infile:
        for line in infile:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if line == ".data":
                in_data_segment = True
                continue
            elif line == ".text":
                in_data_segment = False
                continue
            
            if in_data_segment:
                if ":" in line:
                    label, data = line.split(":", 1)
                    data_segment.append((label.strip(), data.strip()))
            else:
                if line.endswith(":"):
                    labels[line[:-1]] = current_addr
                else:
                    binary = assemble(line)
                    if binary:
                        current_addr += 1
    
    # Second pass: generate binary with resolved labels
    current_addr = 0
    with open(filename, "r") as infile, open("program_output.bin", "w") as outfile:
        for line in infile:
            line = line.strip()
            if not line or line.startswith("#") or line.endswith(":") or line.startswith("."):
                continue
            binary = assemble(line)
            if binary:
                # Resolve labels in branch and jump instructions
                parts = line.strip().split()
                if len(parts) > 1 and parts[-1] in labels:
                    target = parts[-1]
                    if parts[0] in ["beq", "bne", "bgtz"]:
                        offset = labels[target] - current_addr - 1
                        imm_bin = format(offset & 0xFFFF, '016b')
                        binary = binary[:16] + imm_bin
                    elif parts[0] == "jump":
                        addr_bin = format(labels[target] & 0x3FFFFFF, '026b')
                        binary = binary[:6] + addr_bin
                    elif parts[0] == "la":
                        # For load address, we need to find the string label in data segment
                        for str_label, _ in data_segment:
                            if str_label == target:
                                addr_bin = format(len(data_segment) & 0xFFFF, '016b')
                                binary = binary[:16] + addr_bin
                                break
                outfile.write(binary + "\n")
                current_addr += 1

if __name__ == "__main__":
    program_number = sys.argv[1] if len(sys.argv) > 1 else "1"
    input_filename = f"output_basketball{program_number}.asm"
    interpret_file(input_filename)
