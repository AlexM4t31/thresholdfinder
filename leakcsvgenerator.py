import glob 
import pandas as pd 

# let's sketch this bih out 

# it's gonna receive ??what?? as input 
# a fucking directory path, it's just gonna receive a hardcoded directory path as the input 

# then it's gonna fucking read that shit into a csv and spit it out 
# and it is honestly as simple as fucking that dawgg get ur money up 

def tokenizeAndParse(s, sep):
    tokens = []    
    while s.find(sep) != -1:
        tk = s[:s.find(sep)]
        if len(tk) > 0:
            tokens.append(tk) 
        s = s[s.find(sep)+1:]
    if len(s) > 0:
        tokens.append(s)

    parsedTokens = []

    for i in range(0, len(tokens)):
        tmpParsedToken = -999.0
        
        try: 
            tmpParsedToken = float(tokens[i])
        except Exception as e:
            split_single_token = tokens[i].split('-')
            
            try:
                firstNo = int(split_single_token[0])
                secondNo = int(split_single_token[1])

                tmpParsedToken = tokens[i]
            except Exception as secondE:
                pass 

            if tokens[i].find('.png') != -1:
                tmpParsedToken = tokens[i]

        parsedTokens.append(tmpParsedToken)

    return parsedTokens


runExpDirPath = "\\\\data2.thecrick.org\\lab-bentleyk\\home\\users\\mateia\\homogeneous-eight-cell-nine-april-runs"

leakMetricPosition = 132

runData = []

for filePath in glob.glob(runExpDirPath + "\\runs-exp*.txt"):

    fileName = filePath[filePath.rfind("\\")+1:]
    
    dotInd = fileName.find(".")
    paramCombIndex = int(fileName[8:dotInd])

    fullFileName = runExpDirPath + "\\" + fileName

    with open(fullFileName, "r") as file:
        lines = file.readlines()        

        for line in lines:
            line = line.replace("\"", "")
            line = line.replace("\n", "")
            line = line.replace(" ", "")
                        
            line = line[:-1] # remove the last, unnecessary, comma
            # hopefully that comma was not accounted for in the extractTokensIntoList thing,
            # but I'll do a thorough coverage of that anyhow 

            tokens = tokenizeAndParse(line, ",")                                
            
            # 4 things the token processing fct call did: parse, detect and replace invalid vals, update error list, update main list 

            entry = [paramCombIndex] + tokens[0:2] + tokens[leakMetricPosition:leakMetricPosition + 1]

            runData.append(entry)
    
colHeaders = ["combo-id", "inst-id", "file-name", "stripe-thresh-cov-zero"]

df = pd.DataFrame(runData, columns=colHeaders)

# ok we have the actual results themselves but I want to filter out the greater spacing shizz so still have to get the param combos again woopee 

allHeteroParamValues = [[20, 40], [2, 4], [2, 4], [5.25, 6.75,9,12],[20, 40], [2, 4], [2, 4], [5.25, 6.75,9,12], [46,47,48],[54,53,52]]

paramCombos = []

for dw in range(0,2):
    for cid in range(0,2):
        for cil in range(0,2):
            for mr in range(0,4):
                for spacing in range(0,3):
                    tmpNumericalParamCombo = [dw,cid,cil,mr,dw,cid,cil,mr,spacing,spacing]

                    tmpActualParamCombo = []
                    for i in range(0, len(tmpNumericalParamCombo)):
                        tmpActualParamCombo.append(allHeteroParamValues[i][tmpNumericalParamCombo[i]])

                    paramCombos.append(tmpActualParamCombo)
                    
# print(len(paramCombos))

indexedParamCombos = []
for i in range(0, len(paramCombos)):
    e = [i] + paramCombos[i]
    indexedParamCombos.append(e)

paramNames = ["combo-id","division-wait", "normal-div-max-cell-density", "normal-rand-walk-max-cell-density", "normal-random-walk-probability", "division-wait-mutant", "mutant-div-max-cell-density", "mutant-rand-walk-max-cell-density", "mutant-random-walk-probability", "ten-cell-config-left-side-xcor", "ten-cell-config-right-side-xcor"]

paramCombosDf = pd.DataFrame(indexedParamCombos, columns = paramNames)

df = paramCombosDf.merge(df,how="inner", on=["combo-id"])

cellSpacingSubDfs = [ x for _, x in df.groupby(["ten-cell-config-left-side-xcor"]) ] 

finDf = cellSpacingSubDfs[2]

finDf = finDf[["combo-id", "inst-id", "file-name", "stripe-thresh-cov-zero"]]

def addSubDirToFileName(fn):
    return fn[:fn.find('-')] + "/" + fn 

finDf['file-name'] = finDf['file-name'].apply(addSubDirToFileName)

finDf.to_csv("homogeneous-eight-cell-nine-april-exported-extra-smooth-images-df.csv")