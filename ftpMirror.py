import os
import time
import ftplib

class ftpMirror:
    def __init__(self, url, username, password, sourceDir, destDir):
        """A class to mirror an FTP directory to local storage"""
        self.url = url
        self.ftp = ftplib.FTP(url, username, password)
        self.sourceDir = sourceDir
        self.ftp.cwd(sourceDir)
        self.destDir = destDir

        self.ftpDir = []
        self.ftpFiles = []
        self.ftpNumFiles = 0
        self.ftpSizeGB = 0

        self.destFiles = []
        self.destNumFiles = 0
        self.destSizeGB = 0

        self.remainingFiles = 0
        self.remainingGB = 0
        self.exclude = []
        

    def download(self):
        """Main sequence control"""
        print('FTP Mirror Utility: checking directories...')
        self.buildDirList()
        self.checkSource()
        self.buildFileList()
        self.checkDest()

        self.remainingFiles = self.ftpNumFiles - self.destNumFiles
        self.remainingGB = self.ftpSizeGB - self.destSizeGB

        if self.remainingFiles == 0:
            print(f'FTP and {self.destDir} are already synchronized, nothing to downlaod')
            self.exitPrompt()
        else:
            self.preview()

            if self.getDecision():
                self.createDirs()
                startTime = time.time()
                self.transferFiles()
                endTime = (time.time() - startTime) / 60
                print(f'Download Complete, {self.remainingFiles} file(s) in {endTime:.2f} minutes')
                self.exitPrompt()
                
            else:
                print('Exiting without downloading')
                time.sleep(1)


    def buildDirList(self):
        """get all FTP folder names until there are no deeper folders"""
        prevDirNum = -1
        currDirNum = 0
        self.ftpDir = self.ftp.nlst(self.sourceDir)

        while(prevDirNum != currDirNum):
            prevDirNum = len(self.ftpDir)
            for dir in self.ftpDir:
                if self.getNumDirs(dir) != 0:
                    subDirs = self.ftp.nlst(dir)
                    for subDir in subDirs:
                        if subDir not in self.ftpDir:
                            self.ftpDir.append(subDir)
                            currDirNum = len(self.ftpDir)


    def getNumDirs(self, dir):
        """Returns the number of folders in an FTP directory"""
        numDirs = 0
        rows = []
        self.ftp.dir(dir, rows.append)
        
        for i in range(0, len(rows)):
            if self.isDir(rows[i]):
                    numDirs += 1
        return numDirs
    

    def isDir(self, file):
        """Checks if a dir response line is a directory"""
        if '<DIR>' in file:
            return True
        else:
            return False


    def checkSource(self):
        """Computes total FTP file size without excluded file types"""
        for dir in self.ftpDir:
            rows = []
            self.ftp.dir(dir, rows.append)
            for row in range(0, len(rows)):
                temp = self.removeSpaces(list(rows[row].split(' ')))
                if(temp[2] != '<DIR>' and self.noExclusions(temp[-1])):     
                    self.ftpSizeGB += int(temp[2]) / 1000000000
    
        
    def removeSpaces(self, list):
        """Removes the blank spaces from a line of a dir response"""
        noBlanks = [value for value in list if value != '']
        return noBlanks
    

    def noExclusions(self, string):
        """Returns True if no excluded file extensions are present"""
        exclusions = 0
        fileName = string.split('/')
        for exclusion in self.exclude:
            if exclusion in fileName[-1]:
                exclusions += 1
        if exclusions == 0:
            return True
        else:
            return False


    def buildFileList(self):
        """Builds a list of all files in the FTP source directory"""
        for dir in self.ftpDir:
            files = self.ftp.nlst(dir)
            for file in files:
                if self.isFile(file):
                    if self.noExclusions(file):    
                        self.ftpFiles.append(file)
                    
        self.ftpNumFiles = len(self.ftpFiles)
        
        
    def isFile(self, file):
        """Checks if a nlst response line is a file"""
        if (list(file)[-3] == '.' or list(file)[-4] == '.'):
            return True
        else:
            return False

        
    def checkDest(self):
        """Checks which files are already in the destination"""
        for file in self.ftpFiles:
            if os.path.exists(self.destDir + file):
                self.destFiles.append(file)
                self.destSizeGB += os.path.getsize(self.destDir + file) / 1000000000

        self.destNumFiles = len(self.destFiles)
        

    def preview(self):
        """Prints a summary of the files in FTP and local machine"""
        print(f'FTP contains {self.ftpNumFiles} files, {self.ftpSizeGB:.2f} GB')
        print(f'{self.destDir} contains {self.destNumFiles} files, {self.destSizeGB:.2f} GB')
        print(f'Remaining to download: {self.remainingFiles} files, {self.remainingGB:.2f} GB')
        

    def getDecision(self):
        """Get Decision from user to download files"""
        decision = ''
        while(True):
            decision = input('Download all remaining files (y/n): ').upper()
            if decision == 'Y':
                return True
            elif decision == 'N':
                return False
            else:
                print('Invalid input')
                

    def createDirs(self):
        """Mirrors FTP folder structure on local machine"""
        for dir in self.ftpDir:
            if not os.path.exists(self.destDir + dir):
                os.makedirs(self.destDir + dir)


    def transferFiles(self):
        """Copies files from FTP to local machine"""
        for file in self.ftpFiles:              
            path = self.destDir + file

            if os.path.isfile(path):
                if os.path.getsize(path) != self.ftp.size(file):
                    os.remove(path)
                    
            fileName = file.split('/')
            index = self.ftpFiles.index(file) + 1
                
            if not os.path.isfile(path):
                print(f'Transfering file {index} of {self.ftpNumFiles}: {fileName[-1]}', end = '\r')
                with open(path, 'wb') as f:
                    self.ftp.retrbinary('RETR ' + file, f.write)


    def exitPrompt(self):
        """Prompts the user to press enter to exit"""
        input('Press enter to exit: ')
        self.ftp.quit()
        time.sleep(1)         
                

    

        
                    
        















        

