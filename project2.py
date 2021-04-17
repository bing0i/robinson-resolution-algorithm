import sys


def readInputFile(path):
    data = {
        "clauses": [],
        "provingClause": 0,
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


def getShortestClause(data):
    min = 1000000
    minClause = []
    index = 0
    for i, clause in enumerate(data["clauses"]):
        if len(clause) < min:
            min = len(clause)
            minClause = clause[:]
            index = i
    del data["clauses"][index]

    return minClause


def getOppositeClause(clauses, targetClause):
    min = 1000000
    index = 0
    oppositeClause = []
    for targetNum in targetClause:
        for i, clause in enumerate(clauses):
            for num in clause:
                if (
                    targetNum == -num
                    and len(clause) < min
                    and set(clause) != set(targetClause)
                ):
                    oppositeClause = clause[:]
                    min = len(clause)
                    index = i

    return oppositeClause, index


def resolveTwoOppositeClauses(shorterClause, longerClause):
    resultClause = longerClause[:]
    for num1 in shorterClause:
        for num2 in longerClause:
            if num1 + num2 == 0:
                resultClause.remove(num2)

    return resultClause


def solveByResolution(data):
    index = 0
    steps = [data["clauses"][:]]
    while True:
        if len(data["clauses"]) == 1:
            clause1 = data["clauses"][0]
            (clause2, index) = getOppositeClause(data["KB"], clause1)
            del data["clauses"][0]

            if len(clause1) > len(clause2):
                tmpClause = clause1[:]
                clause1 = clause2[:]
                clause2 = tmpClause[:]
            resultClause = resolveTwoOppositeClauses(clause1, clause2)

            data["clauses"].append(resultClause)
            steps.append(data["clauses"][:])

            if len(resultClause) == 0:
                return steps, True

            for clause in data["KB"]:
                if set(resultClause) == set(clause):
                    return steps, False

            data["KB"].append(resultClause)
            continue

        clause1 = getShortestClause(data)
        (clause2, index) = getOppositeClause(data["clauses"], clause1)
        del data["clauses"][index]

        resultClause = resolveTwoOppositeClauses(clause1, clause2)
        if len(resultClause) == 0:
            return steps, True

        data["KB"].append(resultClause)
        data["clauses"].append(resultClause)
        steps.append(data["clauses"][:])

    return steps, False


def convertStepsToCNF(steps):
    CNFSteps = []
    CNFStep = []
    literal = ""
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
