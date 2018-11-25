#!/usr/bin/python
import getopt, sys

config_file = 'config.txt'

def check_change(path):

    print(("file {}  ".format(path)))
    with open(path) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            print("line {}  ".format(cnt))
            print(line)
            line = fp.readline()
            cnt += 1

def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:o", ["config", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        print("Please enter a valid option!!")
        sys.exit(2)
    verbose = False
    for o, a in opts:
        if o in ("-c", "--config"):
            config_file = a
            print("config has changed")
            print(config_file)
        elif o in ("-o", "--output"):
            print ("entered o loop")
            print (config_file)

    check_change(config_file)


if __name__ == "__main__":
    main()

