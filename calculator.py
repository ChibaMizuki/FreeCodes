numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
synbols = ["+", "-", "*", "/"]
calc_formula = input("input formula\n")

formula_nums = []
formula_symbols = []
temp_num = ""
for calc in calc_formula:
    if calc in numbers:
        temp_num += calc
    elif calc in synbols:
        formula_nums.append(int(temp_num))
        formula_symbols.append(calc)
        temp_num = ""
    else:
        continue
formula_nums.append(int(temp_num))

while(len(formula_nums) > 1):
    if "*" in formula_symbols and "/" in formula_symbols:
        idx = min(formula_symbols.index("*"), formula_symbols.index("/"))
    elif "*" in formula_symbols:
        idx = formula_symbols.index("*")
    elif "/" in formula_symbols:
        idx = formula_symbols.index("/")
    else:
        idx = 0
    
    forward = formula_nums.pop(idx)
    backward = formula_nums.pop(idx)
    print(f"{forward} {formula_symbols[idx]} {backward}")
    if formula_symbols[idx] == "+":
        del formula_symbols[idx]
        result = forward + backward
    elif formula_symbols[idx] == "-":
        del formula_symbols[idx]
        result = forward - backward
    elif formula_symbols[idx] == "*":
        del formula_symbols[idx]
        result = forward * backward
    elif formula_symbols[idx] == "/":
        if backward == 0:
            raise ZeroDivisionError
        del formula_symbols[idx]
        result = forward / backward
    formula_nums.insert(idx, result)

print(formula_nums[0])