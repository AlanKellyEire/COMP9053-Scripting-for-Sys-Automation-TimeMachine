import argparse
import os
import datetime
import logging
import fnmatch
from shutil import copyfile

from logging.handlers import RotatingFileHandler

LOG_FILENAME = 'timemachine.log'
rotating_handler = RotatingFileHandler(LOG_FILENAME,
                                       maxBytes=10000000,
                                       backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
rotating_handler.setFormatter(formatter)

logger = logging.getLogger('ass2')
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)


# fileExists function checks if the file passed exists
def fileExists(file):
    return os.path.exists(file)


# addFileToConfig function adds file to the config
def addFileToConfig(file, fileToAdd):
    with open(file, 'a') as appendFile:
        appendFile.write('\n' + fileToAdd)


# existsInFile function checks if the file already exists in config
def existsInFile(file, name):
    lines = readLines(file)
    for line in lines:
        if line.decode('UTF-8').strip('\n') == name:
            return True

    return False


# readlines function reads the lines of the config file
def readLines(configFile):
    try:
        openFile = open(configFile, 'r')
        lines = []

        for line in openFile:
            lines.append(line.rstrip('\r\n').encode('utf-8'))

        return lines
    except:
        logger.error("Could not read from file {0}".format(configFile))
        return None


# removeFile function deleted the file from the config file
def removeFile(configFile, file):
    r = open(configFile, 'rt')
    lines = r.readlines()
    r.close()

    w = open(configFile, 'wt')
    for line in lines:
        if line.strip('\n') != file:
            w.write(line)
    w.close()


# add function checks if file exists in config and adds file to config if it does not
def add(configFile, file):
    if fileExists(file):
        if existsInFile(configFile, file):
            logger.warning("File {0} not added to {1} as it already exists".format(file, configFile))
            print("File {0} not added to {1} as it already exists".format(file, configFile))
        else:
            addFileToConfig(configFile, file)
            print("File {0} added to {1}".format(file, configFile))
            logger.warning("File {0} added to {1}".format(file, configFile))
    else:
        logger.error("File {0} was not added to {1} as it does not exist".format(file, configFile))
        print("File {0} was not added to {1} as it does not exist".format(file, configFile))


# remove function checks if file exists in config and removes file from config if it does
def remove(configFile, file):
    if existsInFile(configFile, file):
        removeFile(configFile, file)
        logger.warning("File {0} has been removed from the {1}".format(file, configFile))
        print("File {0} has been removed from the {1}".format(file, configFile))
    else:
        logger.error("File {0} not removed from {1} as it does not exists in the config file".format(file, configFile))
        print("File {0} not removed from {1} as it does not exists in the config file".format(file, configFile))


# listFiles function gets list of files in the config
def listFiles(configFile):
    files = readLines(configFile)
    return files


# backup function this checks if there is existing copies of the file and if not it backs copies them to the backup location with the modified time appended to the copied filed
def backup(backUpLocation, config):
    # gets list of files to watch
    fileToWatch = listFiles(config)

    for file in fileToWatch:
        # checks if file exists
        exists = os.path.isfile(file)
        if exists:
            mtime_actual = os.path.getmtime(file)
            # converting filename and path to string
            decodedName = file.decode('UTF-8')
            # getting just the filename, removing the path
            filename = decodedName[decodedName.rindex('/') + 1:]
            # adding the backslash to backup path if it does not exist
            if backUpLocation[-1] != '/':
                backPath = backUpLocation + '/'
            else:
                backPath = backUpLocation
            # getting list of current backups in the backup location
            listOfFiles = os.listdir(backPath)
            bool = 0
            for existingFilename in listOfFiles:
                if bool == 0:
                    # checking if any of the backups match this file
                    if fnmatch.fnmatch(str(existingFilename), '*' + filename):
                        # checking if current version of this file is already backed up using the timestamp in the name
                        if str(datetime.datetime.fromtimestamp(mtime_actual)) in existingFilename:
                            bool = 1
                            logger.warning("Backup of File {0} already exists".format(file.decode('UTF-8')))
                        else:
                            bool = 1
                            logger.warning("Backup of File {0} created!!!".format(file.decode('UTF-8')))
                            # coping file to backup loaction if not none of the copies of this file are a backup of the current
                            copyfile(file, backUpLocation + '/' + str(
                                datetime.datetime.fromtimestamp(mtime_actual)) + ' ' + filename)

        else:
            logger.error(
                "Backup of File {0} could not be completed as the file does not exist".format(file.decode('UTF-8')))

        if bool == 0:
            if exists:
                # print("copied", file.decode('UTF-8'))
                logger.warning("First backup of File {0} created!!!".format(file))
                copyfile(file,
                         backUpLocation + '/' + str(datetime.datetime.fromtimestamp(mtime_actual)) + ' ' + filename)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--remove', help='Removes a file from the list of watched files')
    parser.add_argument('-a', '--add', help='Add a new file to be watched')
    parser.add_argument('-l', '--list', action='store_true', help='List all files currently in config file')
    parser.add_argument('-c', '--config', default='config.dat', help='configuration file for files')
    parser.add_argument('-b', '--path', default='./backup_files', help='path of backups location')

    args = parser.parse_args()

    #checks if config exists and creates if not
    if not fileExists(args.config):
        logger.error(
            "config File {0} does not exist".format(args.config))
        try:
            logger.warning(
                "creating config file {0}".format(args.config))
            f = open(args.config, "w+")
            f.close()
        except:
            logger.error(
                "could not create config File {0}".format(args.config))

    # checks if backup directory exists and creates if not
    if not fileExists(args.path):
        logger.error(
            "Backup directory {0} does not exist".format(args.path))
    try:
        logger.warning(
            "creating Backup directory {0}".format(args.path))
        os.mkdir(args.path)
    except:
        logger.error(
            "Could not created backup directory {0}".format(args.path))

    if args.remove:
        remove(args.config, args.remove)
    elif args.add:
        add(args.config, args.add)
    elif args.list:
        for file in listFiles(args.config):
            print(file.decode('UTF-8'))
    elif args.path:
        backup(args.path, args.config)
    else:
        backup(args.path, args.config)  # Calling the main function to start the program
main()
