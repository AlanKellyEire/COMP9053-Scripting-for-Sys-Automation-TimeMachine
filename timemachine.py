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

from logging.handlers import RotatingFileHandler

ALERT_RECORD_FILE = "records_sent.dat"

parser = argparse.ArgumentParser(
    description='Match files for certain matches & run program on matches')
parser.add_argument('-c', '--configfile', default="config.dat",
                    help='file to read the config from')
parser.add_argument('-a', '--alertprog', default=None,
                    help='program to call to generate alerts')

LOG_FILENAME = 'timemachine.log'
rotating_handler = RotatingFileHandler(LOG_FILENAME,
                                       maxBytes=10000000,
                                       backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
rotating_handler.setFormatter(formatter)

logger = logging.getLogger('demoapp')
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)

filesToWatch = {}
logfile = "timemachine.log"


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
        #fileLog = logfile
        #logfile = config_file["log_file"]
        files = populate_files_to_watch(file_paths, config_file["backup_folder"])
        print(files)
        return files
    except:
        logger.error("Config file {0} not found".format(config_file_path))
        print("ERROR!!! with configuration file:", config_file_path )
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
    return files


if len(sys.argv) != 1:
    print(len(sys.argv))
else:
    files = watch_files("config.dat")
    do_initial_copy(files)
