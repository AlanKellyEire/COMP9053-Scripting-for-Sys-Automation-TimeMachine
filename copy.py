import sys


class Copy(object):

    def __init__(self, source_file, destination_file):
        self.file1 = source_file
        self.file2 = destination_file
        contents = self.read_file(self.file1)
        self.create_copy(contents,self.file2)

    def read_file(self, f1):
        #try
        contents = []
        with open(f1) as source_file:
            for line in source_file:
                contents.append(line)
        return contents

    def create_copy(self,source_file_contents,destination_file_path):
        copy_file = open(destination_file_path, "w")
        for line in source_file_contents:
            copy_file.write(str(line))
            #log here
        copy_file.close()
