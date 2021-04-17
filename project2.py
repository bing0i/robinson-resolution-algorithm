import sys


def readInputFile(path):
    data = {
        "clauses": [],
        "provingClause": [],
        "steps": [],
    }
    tmpLine = ""
    with open(path, "r") as inputFile:
        tmpLine = inputFile.readline().rstrip("\n")
        tmpLine = inputFile.readline().rstrip("\n")
        while tmpLine != "ENDKB":
            data["clauses"].append(getClause(tmpLine))
            tmpLine = inputFile.readline().rstrip("\n")
        data["CNFProvingClause"] = inputFile.readline().rstrip("\n")
        data["provingClause"] = getClause(data["CNFProvingClause"])
        data["clauses"].append([-num for num in data["provingClause"]])
        data["KB"] = data["clauses"][:]

    return data


def getClause(str):
    num = 0
    isNegative = False
    i = 0
    clause = []
    while i < len(str):
        if str[i].isalpha():
            num = ord(str[i].lower()) - 96
            if isNegative:
                num = -num
                isNegative = False
        elif str[i] == "~":
            isNegative = True
        elif str[i] == "|":
            clause.append(num)
        i += 1
    clause.append(num)

    return clause


def getShortestClause(clauses, discardedClauses):
    min = 1000000
    minClause = []
    isDuplicate = False

    for clause in clauses:
        if len(clause) < min:
            for discardedClause in discardedClauses:
                if set(discardedClause) == set(clause):
                    isDuplicate = True
                    break

            if not isDuplicate:
                min = len(clause)
                minClause = clause[:]

            isDuplicate = False

    if len(minClause) == 0:
        return None
    return minClause


def getOppositeClause(clauses, targetClause, discardedClauses):
    min = 1000000
    oppositeClause = []
    isDuplicate = False

    for targetNum in targetClause:
        for clause in clauses:
            for num in clause:
                if (
                    targetNum == -num
                    and len(clause) < min
                    and set(clause) != set(targetClause)
                ):
                    for discardedClause in discardedClauses:
                        if set(discardedClause) == set(clause):
                            isDuplicate = True
                            break

                    if not isDuplicate:
                        oppositeClause = clause[:]
                        min = len(clause)

                    isDuplicate = False

    if len(oppositeClause) == 0:
        return None
    return oppositeClause


def resolveTwoOppositeClauses(shorterClause, longerClause):
    resultClause = longerClause[:]
    for num1 in shorterClause:
        for num2 in longerClause:
            if num1 + num2 == 0:
                resultClause.remove(num2)

    return resultClause


def getShorterAndLongerClause(clause1, clause2):
    if len(clause1) < len(clause2):
        shorterClause = clause1[:]
        longerClause = clause2[:]
    else:
        shorterClause = clause2[:]
        longerClause = clause1[:]

    return shorterClause, longerClause


def solveByResolution(data):
    steps = [data["clauses"][:]]
    discardedClauses = []
    isDiscarded = False

    while len(discardedClauses) != len(data["KB"]):
        clause1 = getShortestClause(data["KB"], discardedClauses)
        if clause1 == None:
            return steps, False
        else:
            clause2 = getOppositeClause(data["KB"], clause1, discardedClauses)

        if clause2 == None:
            discardedClauses.append(clause1)
            continue

        (shorterClause, longerClause) = getShorterAndLongerClause(clause1, clause2)
        resultClause = resolveTwoOppositeClauses(shorterClause, longerClause)
        if len(resultClause) == 0:
            return steps, True
        for clause in data["KB"]:
            if set(resultClause) == set(clause):
                discardedClauses.append(longerClause)
                isDiscarded = True
                break

        if not isDiscarded:
            data["KB"].append(resultClause)
            steps.append(data["KB"][:])

        isDiscarded = False

    return steps, False


def convertStepsToCNF(steps):
    CNFSteps = []
    CNFStep = []
    CNFClause = ""
    for step in steps:
        for clause in step:
            for num in clause:
                if num < 0:
                    CNFClause += "~"
                CNFClause += chr(abs(num) + 96) + "|"
            CNFStep.append(CNFClause[:-1])
            CNFClause = ""
        CNFSteps.append(CNFStep)
        CNFStep = []

    return CNFSteps


def writeOutputFile(path, data):
    with open(path, "w") as outputFile:
        outputFile.write(str(data["CNFProvingClause"]) + "\n")

        strSteps = []
        for step in data["CNFSteps"]:
            strSteps.append(",".join(str(clause) for clause in step))

        if strSteps[-1] == "":
            del strSteps[-1]

        for index, step in enumerate(strSteps):
            if step[-1] == ",":
                strSteps[index] = step[:-1]

        outputFile.write("\n".join(str(step) for step in strSteps))
        outputFile.write("\n" + str(data["isProved"]))


if __name__ == "__main__":
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    data = readInputFile(inputPath)
    (steps, data["isProved"]) = solveByResolution(data)
    data["CNFSteps"] = convertStepsToCNF(steps)
    writeOutputFile(outputPath, data)
