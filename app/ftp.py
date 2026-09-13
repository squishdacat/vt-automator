from ftplib import FTP
import os

file = open("password.secret", "r")

FILE_DESTINATION = "/home/michaelw/Documents/vt-automator/videos"
DASHCAM_IP = "10.0.2.34"
FTP_USER = "ftpuser"
FTP_PASSWORD = file.read().replace("\n", "")
file.close()

ftp = FTP(DASHCAM_IP)


def connectToDashcam():
    loginResult = ftp.login(user=FTP_USER, passwd=FTP_PASSWORD)
    if loginResult == "230 Operation successful":
        ftp.set_pasv(True)
    else:
        raise Exception(f"Login unsuccessful: {loginResult}")


def getEventFilesList():
    pwdResult = ftp.pwd
    # Want to make sure that we are actually in the /Event folder before getting files
    if pwdResult != "/Event":
        cwdResult = ftp.cwd("/Event")
        if cwdResult != "250 Operation successful":
            raise Exception("Unable to change to /Event directory")

    files = ftp.nlst()
    return files


def copyEventFiles():
    eventFiles = getEventFilesList()
    for eventFile in eventFiles:
        destFile = os.path.join(FILE_DESTINATION, eventFile)
        with open(destFile, "wb") as file:
            result = ftp.retrbinary(f"RETR {destFile}", file.write)
            print(result)
        break


connectToDashcam()
files = getEventFilesList()
