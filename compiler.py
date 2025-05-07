import sys

memoryAddress = 5000
tRegister = 0
vars = dict()

def getInstructionLine(varName):
    global memoryAddress, tRegister
    tRegisterName = f"r{tRegister}"
    setVariableRegister(varName, tRegisterName)
    returnText = f"addi {tRegisterName}, r0, {memoryAddress}"
    tRegister += 1
    memoryAddress += 4
    return returnText

def setVariableRegister(varName, tRegister):
    global vars
    vars[varName] = tRegister

def getVariableRegister(varName):
    global vars
    return vars.get(varName, "r0")

def getAssignmentLinesImmediateValue(val, varName):
    global tRegister
    outputText = f"addi r{tRegister}, r0, {val}\n"
    outputText += f"steal {getVariableRegister(varName)}, r{tRegister}"
    tRegister += 1
    return outputText

def getAssignmentLinesVariable(varSource, varDest):
    global tRegister
    outputText = ""
    registerSource = getVariableRegister(varSource)
    outputText += f"steal r{tRegister}, {registerSource}\n"
    registerDest = getVariableRegister(varDest)
    outputText += f"steal {registerDest}, r{tRegister}"
    tRegister += 1
    return outputText

program_number = sys.argv[1] if len(sys.argv) > 1 else "1"
input_filename = f"program{program_number}.c"
output_filename = f"output_basketball{program_number}.asm"

try:
    with open(input_filename, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: {input_filename} not found.")
    sys.exit(1)

outputText = ""
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):  # Skip empty lines and comments
        continue

    if line.startswith("if "):
        _, expr = line.split("if ", 1)
        expr = expr.replace("(", "").replace(")", "").replace("{", "")
        outputText += expr + "\n"
    elif line.startswith("}"):
        outputText += "AFTER:\n"
    elif line.startswith("int "):
        parts = line.split()
        var = parts[1].strip(";")
        outputText += getInstructionLine(var) + "\n"
    elif "=" in line:
        parts = line.split()
        if len(parts) >= 3:
            varName, _, val = parts[:3]
            val = val.strip(";")
            if val.isdigit():
                outputText += getAssignmentLinesImmediateValue(val, varName) + "\n"
            else:
                outputText += getAssignmentLinesVariable(val, varName) + "\n"

with open(output_filename, "w") as outputFile:
    outputFile.write(outputText)
