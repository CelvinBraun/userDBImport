import pandas as pd

languages = ["DE", "EN", "FR", "IT", "RU", "PL", "CZ", "SP", "CH", "NL", "BI", "KO", "TW", "PO", "HU", "TR", "RO", "SK",
             "JP", "FI", "VT", "SE", "HR", "US", "AR", "DK", "HE", "GR"]


def readExcelFile():
    with open('config.txt') as f:
        configFilePath = f.readlines()

    stringNoNewLine = []
    for line in configFilePath:
        stringNoNewLine.append(line.replace("\n", ""))

    # read Excel file and ignore the translation row
    excelFile = pd.read_excel(stringNoNewLine[1], skiprows=[1])

    # throw out "nan" values
    excelFile = excelFile.fillna('')

    userList = []
    itemList = []
    rowList = []

    for rowHeader in excelFile:
        rowList.append(rowHeader)

    # goes through the rows
    for row in excelFile.values:
        # goes through the items of a row
        for item in range(len(row)):
            itemList.append({rowList[item]: row[item]})

        userList.append(itemList)
        itemList = []

    return userList


# clean data from irregularities
def cleanData():
    data = readExcelFile()
    userData = []
    cleanerData = []

    # go through users
    for user in data:

        noError = True

        # go through the data from each user
        for value in user:
            keyValue = list(value.keys())[0]
            dictValue = list(value.values())[0]

            if isinstance(dictValue, float):
                dictValue = int(dictValue)

            # check for rows where can cause issues.....
            if keyValue == "Benutzer" and len(dictValue) == 0:
                noError = False
            if keyValue == "Sprache" and dictValue not in languages:
                noError = False
            if keyValue == "Pin" and len(str(dictValue)) == 0:
                noError = False

            userData.append({keyValue: dictValue})

        # only append when no issues
        if noError:
            cleanerData.append(userData)
        userData = []

    return cleanerData
