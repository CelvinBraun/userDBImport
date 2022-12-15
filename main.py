import pyodbc
import time
import os
import encrypt
import excelData


# database connection global
with open('config.txt') as f:
    configFilePath = f.readlines()

stringNoNewLine = []
for line in configFilePath:
    stringNoNewLine.append(line.replace("\n", ""))

password = os.environ.get('dbUserPassword')

# build string for database connection
conn_str = "DRIVER=" + stringNoNewLine[3] + ";" + "SERVER=" + stringNoNewLine[5] + ";" + "DATABASE=" \
           + stringNoNewLine[7] + ";" + "USERNAME=" + stringNoNewLine[9] \
           + ";" + "PASSWORD=" + password + ";" + "Trusted_Connection=yes; "

cnxn = pyodbc.connect(conn_str)


def encyptData():
    data = excelData.cleanData()

    # go through users
    for user in data:

        # go through the data from each user
        for value in user:
            keyValue = list(value.keys())[0]
            dictValue = list(value.values())[0]

            if str(dictValue) != "" and keyValue == "Passwort" or keyValue == "Pin":
                encryptedValue = encrypt.createEncryptedValue(dictValue)
                value.update({keyValue: encryptedValue})

    # updated encrypted data
    return data


def compareWithCurrentUserData(data):
    usersToImport = []
    currentUsers = []

    cursor = cnxn.cursor()
    cursor.execute("SELECT Benutzer, Passwort, Pin FROM tblBenutzer")

    # create list with current user data
    for row in cursor.fetchall():
        currentUsers.append(list(row))

    # compare with Excel data
    for user in data:
        noDataExists = True

        # go through the data from each user
        for value in user:
            keyValue = list(value.keys())[0]
            dictValue = list(value.values())[0]

            if dictValue != "" and keyValue == "Passwort" or keyValue == "Pin":

                for users in currentUsers:
                    if dictValue in users:
                        noDataExists = False

        if noDataExists:
            usersToImport.append(user)

    return usersToImport


# returns highest id in tblBenutzer
def getHighestID():
    cursor = cnxn.cursor()
    cursor.execute("SELECT max(id) FROM tblBenutzer")

    return cursor.fetchall()[0][0]


def commitNewUsers(data):
    highestID = getHighestID()
    dataForLog = []

    for user in data:
        rowsToImport = ""
        valuesToImport = ""
        highestID += 1

        for value in user:
            keyValue = list(value.keys())[0]
            dictValue = list(value.values())[0]

            # create string for which rows get imported
            if rowsToImport == "":
                rowsToImport = "ID, " + keyValue
            else:
                rowsToImport += ", " + keyValue

            # create string for which values get imported -> id is raising on initial build
            if valuesToImport == "":
                if isinstance(dictValue, int):
                    valuesToImport = str(highestID) + "," + str(dictValue)
                else:
                    valuesToImport = str(highestID) + "," + "\'" + str(dictValue) + "\'"

            else:
                if isinstance(dictValue, int):
                    valuesToImport += "," + str(dictValue)
                else:
                    valuesToImport += "," + "\'" + str(dictValue) + "\'"

        cursor = cnxn.cursor()
        commitString = "INSERT INTO tblBenutzer (" + rowsToImport + ") VALUES (" + valuesToImport + ")"
        dataForLog.append(commitString)

        cursor.execute(commitString)
        cnxn.commit()

    return dataForLog


def createLog(data):
    with open("logs\\" + time.strftime("%Y%m%d-%H%M%S")+".txt", 'w', encoding="utf-8") as f:
        for item in data:
            f.write("%s\n" % item)


def deleteExcelFile(file):
    os.remove(file)


def checkIfFileExists(file):
    return os.path.isfile(file)


if checkIfFileExists(stringNoNewLine[1]):
    # receive data from excelData.py and encrypt it. compare afterwards with current user in database.
    importData = compareWithCurrentUserData(encyptData())
    print(importData)
    # import users, where got checked from before. save the infos about the users to a variable for log.
    gotImported = commitNewUsers(importData)

    # create log file, when enabled
    if stringNoNewLine[11] == "True":
        createLog(gotImported)
    # delete Excel file
    deleteExcelFile(stringNoNewLine[1])