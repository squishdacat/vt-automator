from ftplib import FTP
from ftplib import error_perm
import os


class Dashcam:
    def __init__(self, ip: str, user: str, passwordFile: str = "", password: str = ""):
        self.ip: str = ip
        self.user: str = user
        self.password: str = "unset"
        if password != "":
            self.password = password
        else:
            if passwordFile != "":
                with open(passwordFile, "r") as file:
                    self.password = file.read().replace("\n", "")
            else:
                raise Exception("No password provided for dashcam")
        print(f"Dashcam details user: {user} password: {password}")

        self.ftp: FTP = FTP()

    def login(self) -> None:
        try:
            voidcmdResult = self.ftp.voidcmd("NOOP")
            if voidcmdResult == "200 Operation successful":
                return
        except AttributeError:
            connectResult = self.ftp.connect(self.ip)

            if connectResult == "220 Operation successful":
                loginResult = self.ftp.login(user=self.user, passwd=self.password)
                if loginResult == "230 Operation successful":
                    self.ftp.set_pasv(True)
                    return
                else:
                    raise Exception(f"Login unsuccessful: {loginResult}")
        except error_perm as e:
            if e.args[0] == "530 Login with USER and PASS":
                print("running")
                loginResult = self.ftp.login(user=self.user, passwd=self.password)
                if loginResult == "230 Operation successful":
                    self.ftp.set_pasv(True)
                    return
                else:
                    raise Exception(f"Login unsuccessful: {loginResult}")
        except:
            print("Unhandled error occurred")

    def getEventFilesList(self):
        self.login()
        pwdResult = self.ftp.pwd
        # Want to make sure that we are actually in the /Event folder before getting files
        if pwdResult != "/Event":
            cwdResult = self.ftp.cwd("/Event")
            if cwdResult != "250 Operation successful":
                raise Exception("Unable to change to /Event directory")

        files = self.ftp.nlst()
        return files

    def downloadEventFiles(
        self, fileDestination: str, deleteFiles: bool = True
    ) -> list[dict[str, str]]:
        self.login()
        eventFiles = self.getEventFilesList()
        downloadResults = []
        numberEventFiles = len(eventFiles)
        for i, eventFile in enumerate(eventFiles):
            destFile = os.path.join(fileDestination, eventFile)
            print(f"[{i}/{numberEventFiles}]: {destFile}")
            with open(destFile, "wb") as file:
                result = self.ftp.retrbinary(f"RETR {eventFile}", file.write)
                deleteResult = "N/A"

                if result == "226 Operation successful" and deleteFiles:
                    deleteResult = self.ftp.delete(eventFile)

                resultDiagnostic = {
                    "file": eventFile,
                    "copyResult": result,
                    "deleteResult": deleteResult,
                }
                downloadResults.append(resultDiagnostic)

            if i == 5:
                break
        return downloadResults
