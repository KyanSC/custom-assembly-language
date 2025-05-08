import sys
import re

#python compiler.py 1 to run program1, python compiler.py 2 to run program2, etc.

memoryAddress = 5000
tRegister = 0
vars = dict()
labelCounter = 0
stringCounter = 0

def getNewLabel():
    global labelCounter
    label = f"L{labelCounter}"
    labelCounter += 1
    return label

def getNewStringLabel():
    global stringCounter
    label = f"STR{stringCounter}"
    stringCounter += 1
    return label

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
    output_reg = f"r{tRegister}"
    tRegister += 1
    if varName:
        outputText += f"steal r{getVariableRegister(varName)}, {output_reg}\n"
    return outputText, output_reg

def getAssignmentLinesVariable(varSource, varDest=None):
    global tRegister
    outputText = f"steal r{tRegister}, r{getVariableRegister(varSource)}\n"
    output_reg = f"r{tRegister}"
    tRegister += 1
    if varDest:
        outputText += f"steal r{getVariableRegister(varDest)}, {output_reg}\n"
    return outputText, output_reg

def compileModulo(value, modulus):
    global tRegister
    # Load value into register
    if isinstance(value, str) and value in vars:
        output = f"steal r{tRegister}, {getVariableRegister(value)}\n"
    else:
        output = f"addi r{tRegister}, r0, {value}\n"
    value_reg = f"r{tRegister}"
    tRegister += 1
    
    # Load modulus into register
    output += f"addi r{tRegister}, r0, {modulus}\n"
    mod_reg = f"r{tRegister}"
    tRegister += 1
    
    # Perform division and get remainder
    output += f"div {value_reg}, {mod_reg}\n"
    output += f"mfhi r{tRegister}\n"
    result_reg = f"r{tRegister}"
    tRegister += 1
    
    return output, result_reg

def compileForLoop(loopVar, startVal, endVal, body):
    global tRegister
    startLabel = getNewLabel()
    endLabel = getNewLabel()
    
    # Initialize loop variable
    output, _ = getAssignmentLinesImmediateValue(startVal, loopVar)
    output += f"\n{startLabel}:\n"
    
    # Check loop condition
    # Load loop variable into register
    output_load, loop_reg = getAssignmentLinesVariable(loopVar)
    output += output_load
    
    # Load end value into register
    output_end, end_reg = getAssignmentLinesImmediateValue(endVal, None)
    output += output_end
    
    # Compare loop variable with end value
    output += f"sub r{tRegister}, {end_reg}, {loop_reg}\n"
    output += f"bgtz r{tRegister}, {endLabel}\n"
    tRegister += 1
    
    # Loop body
    output += body
    
    # Increment loop variable
    # Load current value
    output_load, curr_reg = getAssignmentLinesVariable(loopVar)
    output += output_load
    
    # Add 1
    output += f"addi r{tRegister}, {curr_reg}, 1\n"
    inc_reg = f"r{tRegister}"
    tRegister += 1
    
    # Store back
    output += f"steal {getVariableRegister(loopVar)}, {inc_reg}\n"
    
    # Jump back to start
    output += f"jump {startLabel}\n"
    output += f"{endLabel}:\n"
    
    return output

def compileIfElse(condition, ifBody, elseBody=None):
    global tRegister
    elseLabel = getNewLabel()
    endLabel = getNewLabel()
    
    # Parse condition
    if condition is None:
        return ifBody  # For else blocks
    
    output = ""
    if "==" in condition:
        left, right = condition.split("==")
        left = left.strip()
        right = right.strip()
        
        # Load left value
        if left in vars:
            output_left, left_reg = getAssignmentLinesVariable(left)
            output += output_left
        else:
            output_left, left_reg = getAssignmentLinesImmediateValue(left, None)
            output += output_left
        
        # Load right value
        output_right, right_reg = getAssignmentLinesImmediateValue(right, None)
        output += output_right
        
        # Compare
        output += f"sub r{tRegister}, {left_reg}, {right_reg}\n"
        output += f"bne r{tRegister}, r0, {elseLabel if elseBody else endLabel}\n"
        tRegister += 1
        
    elif "%" in condition:
        # Parse modulo expression
        match = re.match(r'(.*?)\s*%\s*(\d+)\s*==\s*(\d+)', condition)
        if match:
            left = match.group(1).strip()
            modulus = match.group(2)
            expected = match.group(3)
            
            # Calculate modulo
            modOutput, resultReg = compileModulo(left, modulus)
            output += modOutput
            
            # Compare with expected value
            output_exp, exp_reg = getAssignmentLinesImmediateValue(expected, None)
            output += output_exp
            
            output += f"sub r{tRegister}, {resultReg}, {exp_reg}\n"
            output += f"bne r{tRegister}, r0, {elseLabel if elseBody else endLabel}\n"
            tRegister += 1
    
    # If body
    output += ifBody
    
    if elseBody:
        output += f"jump {endLabel}\n"
        output += f"{elseLabel}:\n"
        output += elseBody
    
    output += f"{endLabel}:\n"
    return output

def compilePrint(value):
    global tRegister
    if value.startswith('"'):
        # String literal
        strLabel = getNewStringLabel()
        output = f".data\n{strLabel}: .asciiz {value}\n.text\n"
        output += f"la r{tRegister}, {strLabel}\n"
        output += f"print r{tRegister}\n"
        tRegister += 1
    elif value.isdigit():
        # Numeric literal
        output = f"addi r{tRegister}, r0, {value}\n"
        output += f"print r{tRegister}\n"
        tRegister += 1
    else:
        # Variable
        output = f"steal r{tRegister}, {getVariableRegister(value)}\n"
        output += f"print r{tRegister}\n"
        tRegister += 1
    return output

program_number = sys.argv[1] if len(sys.argv) > 1 else "1"
input_filename = f"program{program_number}.c"
output_filename = f"output_basketball{program_number}.asm"

try:
    with open(input_filename, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: {input_filename} not found.")
    sys.exit(1)

outputText = ".text\n"  # Start in text segment
currentBlock = []
inIfBlock = False
inElseBlock = False
ifCondition = None
braceCount = 0
loopBody = []

def processIfBlock(lines, start_idx):
    braceCount = 1
    blockLines = []
    i = start_idx + 1
    while i < len(lines) and braceCount > 0:
        line = lines[i].strip()
        if "{" in line:
            braceCount += 1
        if "}" in line:
            braceCount -= 1
        if braceCount > 0:
            blockLines.append(line)
        i += 1
    return blockLines, i

for i, line in enumerate(lines):
    line = line.strip()
    if not line or line.startswith("#"):  # Skip empty lines and comments
        continue

    if line.startswith("int "):
        # Variable declaration
        varName = line.split()[1].replace(";", "")
        setVariableRegister(varName, tRegister)
        tRegister += 1
    elif "=" in line and not line.startswith("for "):
        # Variable assignment
        parts = line.split("=")
        left = parts[0].strip()
        right = parts[1].strip().replace(";", "")
        
        if "+" in right:
            # Addition
            operands = right.split("+")
            left_op = operands[0].strip()
            right_op = operands[1].strip()
            
            # Load left operand
            output_left, left_reg = getAssignmentLinesVariable(left_op)
            outputText += output_left
            
            # Load right operand
            output_right, right_reg = getAssignmentLinesVariable(right_op)
            outputText += output_right
            
            # Add them
            outputText += f"add r{tRegister}, {left_reg}, {right_reg}\n"
            result_reg = f"r{tRegister}"
            tRegister += 1
            
            # Store result
            outputText += f"steal {getVariableRegister(left)}, {result_reg}\n"
        else:
            # Simple assignment
            if right.isdigit():
                # Immediate value
                output, _ = getAssignmentLinesImmediateValue(right, left)
                outputText += output
            else:
                # Variable to variable
                output, _ = getAssignmentLinesVariable(right, left)
                outputText += output
    elif line.startswith("print("):
        # Print statement
        value = line.split("print(")[1].split(")")[0].strip()
        outputText += compilePrint(value)
    elif line.startswith("for "):
        # For loop handling (existing code)
        parts = line.split("for ")[1].split(";")
        init = parts[0].strip()
        condition = parts[1].strip()
        increment = parts[2].strip().replace(")", "")
        
        loopVar = init.split("=")[0].strip().split()[1]
        startVal = int(init.split("=")[1].strip())
        endVal = int(condition.split("<=")[1].strip())
        
        # Initialize loop variable register
        setVariableRegister(loopVar, tRegister)
        tRegister += 1
        
        # Read loop body
        braceCount = 1
        loopBody = []
        j = i + 1
        while braceCount > 0 and j < len(lines):
            if "{" in lines[j]:
                braceCount += 1
            if "}" in lines[j]:
                braceCount -= 1
            if braceCount > 0:
                loopBody.append(lines[j])
            j += 1
        
        # Process loop body
        bodyText = ""
        k = 0
        while k < len(loopBody):
            bodyLine = loopBody[k].strip()
            if "print" in bodyLine:
                value = bodyLine.split("print(")[1].split(")")[0].strip()
                if value.startswith('"'):
                    bodyText += compilePrint(value)
                else:
                    bodyText += compilePrint(value)
                k += 1
            elif "if " in bodyLine:
                # Extract if condition
                ifCondition = bodyLine.split("if ")[1].strip().replace("{", "").strip()
                
                # Get if block
                ifBlock = []
                l = k + 1
                braceCount = 1
                while l < len(loopBody) and braceCount > 0:
                    if "{" in loopBody[l]:
                        braceCount += 1
                    if "}" in loopBody[l]:
                        braceCount -= 1
                    if braceCount > 0:
                        ifBlock.append(loopBody[l])
                    l += 1
                
                # Process if block
                ifBlockText = ""
                for blockLine in ifBlock:
                    if "print" in blockLine:
                        value = blockLine.split("print(")[1].split(")")[0].strip()
                        if value.startswith('"'):
                            ifBlockText += compilePrint(value)
                        else:
                            ifBlockText += compilePrint(value)
                
                # Look for else if or else
                elseBlockText = None
                if l < len(loopBody) and "else" in loopBody[l]:
                    elseBlock = []
                    l += 1
                    braceCount = 1
                    while l < len(loopBody) and braceCount > 0:
                        if "{" in loopBody[l]:
                            braceCount += 1
                        if "}" in loopBody[l]:
                            braceCount -= 1
                        if braceCount > 0:
                            elseBlock.append(loopBody[l])
                        l += 1
                    
                    elseBlockText = ""
                    for blockLine in elseBlock:
                        if "print" in blockLine:
                            value = blockLine.split("print(")[1].split(")")[0].strip()
                            if value.startswith('"'):
                                elseBlockText += compilePrint(value)
                            else:
                                elseBlockText += compilePrint(value)
                
                # Parse modulo condition
                if "%" in ifCondition:
                    match = re.match(r'(.*?)\s*%\s*(\d+)\s*==\s*(\d+)', ifCondition)
                    if match:
                        left = match.group(1).strip()
                        modulus = match.group(2)
                        expected = match.group(3)
                        
                        # Calculate modulo
                        modOutput, resultReg = compileModulo(left, modulus)
                        bodyText += modOutput
                        
                        # Compare with expected value
                        output_exp, exp_reg = getAssignmentLinesImmediateValue(expected, None)
                        bodyText += output_exp
                        
                        bodyText += f"sub r{tRegister}, {resultReg}, {exp_reg}\n"
                        bodyText += f"bne r{tRegister}, r0, {getNewLabel()}\n"
                        tRegister += 1
                
                bodyText += compileIfElse(ifCondition, ifBlockText, elseBlockText)
                k = l
            else:
                k += 1
        
        outputText += compileForLoop(loopVar, startVal, endVal, bodyText)

with open(output_filename, "w") as outputFile:
    outputFile.write(outputText)
