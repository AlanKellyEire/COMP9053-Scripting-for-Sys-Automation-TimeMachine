import argparse
import copy
import yaml
import os
import datetime
import logging
import sys
import fnmatch
from shutil import copyfile

from logging.handlers import RotatingFileHandler

# parser.add_argument('-l','--list', action="store_true",
# help='Print a list of the file being observed')

LOG_FILENAME = 'timemachine.log'
rotating_handler = RotatingFileHandler(LOG_FILENAME,
                                       maxBytes=10000000,
                                       backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
rotating_handler.setFormatter(formatter)

logger = logging.getLogger('ass2')
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)

def help():
    print ("HELP SECTION")
    print("Usage: python3 timemachine.py [OPTION...] [FILE]...")
    print("")
    print("  -b     [BACKUPPATH]   option used to add another backup path, full path must be provided if not in current directory ")
    print("  -l                    lists all the files to be watched")
    print("  -c     [CONFIGFILE]   option used to add another config file, full path must be provided if not in current directory ")
    print("  -a     [FILETOADD]    option used to add another file to config file, full path must be provided if not in current directory")
    print("  -a     [FILETOREMOVE] option used to remove file from config file, path must be identical to that in the config file")
    print("  -h                    print help message")
    print("")
    print("")
    print("EXAMPLE of use:")
    print("")
    print("python3 timemachine.py -c config.dat                 use config.dat as the config file")
    print("python3 timemachine.py -b ./backups                  use the directory backups as the backups location")
    print("python3 timemachine.py -r ./result.yml               remove /result.yml from files to watch")
    print("python3 timemachine.py -a ./result.yml               add /result.yml to files to watch")
    print("python3 timemachine.py -l                            list all files being watched")
    print("")
    print("")
    print("GNU 'backup'")


def fileExists(file):
    return os.path.exists(file)


def addFileToConfig(file, newLine):
    with open(file, 'a') as appendFile:
        appendFile.write('\n' + newLine)


def existsInFile(file, search):
    lines = readLines(file)
    for line in lines:
        if line.decode('UTF-8').strip('\n') == search:
            return True

    return False


def readLines(file):
    try:
        openFile = open(file, 'r')
        lines = []

        for line in openFile:
            lines.append(line.rstrip('\r\n').encode('utf-8'))

        return lines
    except:
        return None


def removeLineFromFile(file, removeLine):
    r = open(file, 'rt')
    lines = r.readlines()
    r.close()

    w = open(file, 'wt')
    for line in lines:
        if line.strip('\n') != removeLine:
            w.write(line)
    w.close()


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


def remove(configFile, file):
    if existsInFile(configFile, file):
        removeLineFromFile(configFile, file)
        logger.warning("File {0} has been removed from the {1}".format(file, configFile))
        print("File {0} has been removed from the {1}".format(file, configFile))
    else:
        logger.error("File {0} not removed from {1} as it does not exists in the config file".format(file, configFile))
        print("File {0} not removed from {1} as it does not exists in the config file".format(file, configFile))

def listFiles(configFile):
    files = readLines(configFile)
    return files


def backup(storePath, config):
    watching = listFiles(config)

    for file in watching:

        exists = os.path.isfile(file)
        if exists:
            mtime_actual = os.path.getmtime(file)

            decodedName = file.decode('UTF-8')
            filename = decodedName[decodedName.rindex('/') + 1:]

            if storePath[-1] != '/':
                backPath = storePath + '/'
            else:
                backPath = storePath
            listOfFiles = os.listdir(backPath)
            bool = 0
            for existingFilename in listOfFiles:
                if bool == 0:
                    if fnmatch.fnmatch(str(existingFilename), '*' + filename):

                        if str(datetime.datetime.fromtimestamp(mtime_actual)) in existingFilename:
                            bool = 1
                            logger.warning("Backup of File {0} already exists".format(file.decode('UTF-8')))
                        else:
                            bool = 1
                            logger.warning("Backup of File {0} created!!!".format(file.decode('UTF-8')))
                            copyfile(file, storePath + '/' + str(
                                datetime.datetime.fromtimestamp(mtime_actual)) + ' ' + filename)

        else:
            logger.error(
                "Backup of File {0} could not be completed as the file does not exist".format(file.decode('UTF-8')))

        if bool == 0:
            if exists:
                print("copied", file.decode('UTF-8'))
                logger.warning("First backup of File {0} created!!!".format(file))
                copyfile(file, storePath + '/' + str(datetime.datetime.fromtimestamp(mtime_actual)) + ' ' + filename)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--remove', help='Removes a file from the list of watched files')
    parser.add_argument('-a', '--add', help='Add a new file to be watched')
    parser.add_argument('-l', '--list', action='store_true', help='List all files currently in config file')
    parser.add_argument('-c', '--config', default='config.dat', help='configuration file for files')
    parser.add_argument('-b', '--path', default='./backup_files', help='path of backups location')
    parser.add_argument('-h', '--help', help='provide help message')

    args = parser.parse_args()

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
        backup(args.path, args.config)
        print('File is not in config file, Skipping remove')


main()
