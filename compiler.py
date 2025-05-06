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

with open("program1.c", "r") as f:
    lines = f.readlines()

outputText = ""
for line in lines:
    line = line.strip()
    if line.startswith("if "):
        _, expr = line.split("if ")
        expr = expr.replace("(", "").replace(")", "").replace("{", "")
        outputText += expr + "\n"
    elif line.startswith("}"):
        outputText += "AFTER:\n"
    elif line.startswith("int "):
        _, var = line.split()
        var = var.strip(";")
        outputText += getInstructionLine(var) + "\n"
    elif "=" in line:
        varName, _, val = line.split()
        val = val.strip(";")
        if val.isdigit():
            outputText += getAssignmentLinesImmediateValue(val, varName) + "\n"
        else:
            outputText += getAssignmentLinesVariable(val, varName) + "\n"

with open("output_basketball.asm", "w") as outputFile:
    outputFile.write(outputText)
