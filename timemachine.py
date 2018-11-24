import argparse
import copy
import yaml
import os
import datetime
import re
import pickle
import sys
import subprocess
import logging
import sys
import glob

from logging.handlers import RotatingFileHandler

# parser.add_argument('-l','--list', action="store_true",
# help='Print a list of the file being observed')

LOG_FILENAME = 'timemachine.log'
rotating_handler = RotatingFileHandler(LOG_FILENAME,
                                       maxBytes=10000000,
                                       backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
rotating_handler.setFormatter(formatter)

logger = logging.getLogger('demoapp')
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)


def read_config(filename):
    try:
        logger.debug("Reading config from {0}".format(filename))
        with open(filename, "r") as f:
            first_line = f.readline()
            print(first_line)
            return yaml.load(f)
    except FileNotFoundError:
        logger.error("Config file {0} not found".format(filename))
        print("Config file {0} not found".format(filename), file=sys.stderr)
        sys.exit(1)


def list_of_files(self, config_files):
    file_paths = []
    for folders in config_files:
        path = folders["folder_path"]
        watch = folders["files"]
        for w in watch:
            file_paths.append("{0}/{1}".format(path, w))
            # print("{0}/{1}".format(path, w))
    return file_paths


def do_initial_copy(files):
    for copy_file in files.keys():
        if files[copy_file]["last_copied"] == "not_copied":
            print("copy_file")
            copy.Copy(copy_file, files[copy_file]["copy_path"])
            files[copy_file]["last_copied"] = files[copy_file]["modified"]
        else:
            print("any hit")
    return files


def read(filename):
    try:
        # logger.debug("Reading config from {0}".format(filename))
        with open(filename, "r") as f:
            first_line = f.readline()
            print(first_line)
            return yaml.load(f)
    except FileNotFoundError:
        # logger.error("Config file {0} not found".format(filename))
        print("Config file {0} not found".format(filename), file=sys.stderr)
        sys.exit(1)


def list_of_files(config_files):
    file_paths = []
    for folders in config_files:
        path = folders["folder_path"]
        watch = folders["files"]
        for w in watch:
            file_paths.append("{0}/{1}".format(path, w))
            # print("{0}/{1}".format(path, w))
    return file_paths


def watch_files(config_file_path):
    try:
        logger.debug("Reading config from {0}".format(config_file_path))
        config_file = read(config_file_path)
        file_paths = list_of_files(config_file["watch"])
        print(file_paths)
        print(config_file)
        # fileLog = logfile
        # logfile = config_file["log_file"]
        files = populate_files_to_watch(file_paths, config_file["backup_folder"])
        print(files)
        return files
    except:
        logger.error("Config file {0} not found".format(config_file_path))
        print("ERROR!!! with configuration file:", config_file_path)
        sys.exit(1)


def populate_files_to_watch(source_files, dest_path):
    files = filesToWatch
    print(files)
    for file in source_files:
        timestamp = os.path.getmtime(file)
        if file not in files.keys():
            files.update({file: {"modified": timestamp,
                                 "last_copied": "not_copied",
                                 "copy_path": "{0}/{1}-{2}".format(dest_path,
                                                                   datetime.datetime.fromtimestamp(timestamp),
                                                                   os.path.basename(file))
                                 }
                          })
        else:
            files[file]["modified"] = os.path.getmtime(file)
            files[file]["copy_path"] = "{0}/{1}-{2}".format(dest_path, datetime.datetime.fromtimestamp(timestamp),
                                                            os.path.basename(file))
    with open('result.yml', 'w') as yaml_file:
        yaml.dump(files, yaml_file, default_flow_style=False)
    return files


def copy(path, config_file):
    watching = ConfigurationService().getFilesToWatch(path, config_file)

    for file in watching:
        if fileExists(file.getPath()):
            if file.isFileChanged():
                CopyService().copyFileSnapshot(file)
        else:
            print('Warning: ' + file.getPath().decode('UTF-8') + ' does not exist, skipping')


def loadBackUpData(backupData_file):
    try:
        with open(backupData_file, 'r') as f:
            filesToWatch = yaml.load(f)
        logger.debug("Reading config from {0}".format(backupData_file))
    except:
        logger.error("Config file {0} not found".format(backupData_file))


def read_config(filename):
    try:
        logger.debug("Reading config from {0}".format(filename))
        with open(filename, "r") as f:
            first_line = f.readline()
            print(first_line)
            return yaml.load(f)
    except FileNotFoundError:
        logger.error("Config file {0} not found".format(filename))
        print("Config file {0} not found".format(filename), file=sys.stderr)
        sys.exit(1)


def create_copy(self, source_file_contents, destination_file_path):
    copy_file = open(destination_file_path, "w")
    for line in source_file_contents:
        copy_file.write(str(line))
        # log here
    copy_file.close()


############ do not delete
def fileExists(file):
    return os.path.exists(file)


def addFileToConfig(file, newLine):
    with open(file, 'a') as appendFile:
        appendFile.write('\n' + newLine)


def existsInFile(file, search):
    lines = readLines(file)
    for line in lines:
        if line == search:
            return True

    return False


def readLines(file):
    try:
        openFile = open(file, 'r')
        lines = []

        for line in openFile:
            lines.append(line.rstrip('\r\n').encode('utf-8'))

        return lines
    except IOError:
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
            logger.debug("File {0} not added to config as it already exists".format(file))
        else:
            addFileToConfig(configFile, file)
            logger.debug("File {0} added to config".format(file))
    else:
        print('Unable to add, File does not exist')


def remove(configFile, file):
    if existsInFile(configFile, file):
        removeLineFromFile(configFile, file)
        logger.debug("File {0} has been removed from the config".format(file))
    else:
        logger.debug("File {0} not removed from config as it does not exists".format(file))
        print("File {0} not removed from config as it does not exists".format(file))


def listFiles(configFile):
    files = readLines(configFile)
    #for file in files:
     #   print(file)
    return files


def backup(storePath, config):
    watching = listFiles(config)
#
#     for file in watching:
#         print("file ", file)
#         exists = os.path.isfile(file)
#         if exists:
#             mtime_actual = os.path.getmtime(file)
#             # backUps = [
#             filename = file[file.rindex('/')+1:]
#             print(filename)
#             for name in glob.glob(storePath + "*" + filename):
#                 print
#                 '\t', name
#                 # backups = [fn for fn in os.listdir(storePath)
#     # if any(fn.endswith(ext) for ext in file)]
#     # if mtime_actual not in backups:
#     #     newName = storePath + mtime_actual + ' : ' + file
#     #     copy.Copy(file, newName)
#
#         else:
#             print ("tesrt")
#             #print('Warning: ' + file.getPath().decode('UTF-8') + ' does not exist, skipping')  # def getFiles(backUpLoc, configFile):
#
#
# #         files = readLines(configFile)
# #         watchingFiles = []
# #         n = 1
# #         for file in files:
# #             # print(n)
# #             # print(file)
# #             # n += 1
# #             watchingFiles.append(file)
# #         print(watchingFiles)
# #         return watchingFiles

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-r', '--remove', help='Removes a file from the list of watched files')
    parser.add_argument('-a', '--add', help='Add a new file to be watched')
    parser.add_argument('-l', '--list', action='store_true', help='List all files currently in config file')
    parser.add_argument('-c', '--config', default='config.dat', help='configuration file for files')
    parser.add_argument('-b', '--path', default='./backup_files', help='path of backups location')

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
