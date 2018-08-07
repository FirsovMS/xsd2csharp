#!/usr/bin/python

import os
import subprocess
import shutil

# Generator generate *.cs from *.xsd files
class Generator:
    def __init__(self):
        self.path_in = ".";
        # path_out folder has name as base folder
        split_char = "\\" if os.name == "nt" else "/";
        self.path_out = os.getcwd().split(split_char)[-1].split('.')[0] 
        self.cmd = "Xsd2Code {} {} {} -o /pl Net35 /xa+ /if-";
        self.namespace = "TravelSkyDLL.Lib.XML";
        self.files = list();
        self.file_tree = list(); # pair { path, filename }  path + "/" + filename = full path
        self.analyzer = Analyze(self.file_tree);

    @property
    def get_path_out(self):
        return self.path_out;

    @property
    def get_file_tree(self):
        return self.file_tree;    

    def print_dialog(self):
        base = input("Enter base namespace: (example and default :'{}'): ".format(self.namespace));
        if base: self.namespace = base;
        print("Choosed cmd: {}".format(self.cmd.format("'<file>'", self.namespace, "'<output_name>'")));

    def get_files(self):
        print("Log: Get files to procede");
        for file in os.listdir(self.path_in):
            if file.endswith(".xsd"): self.files.append(file);
        if  len(self.files) == 0:
            print("Files not exists in dir:{}!".format(self.path_in));
            exit(-1);
        print("File Count : {}".format(len(self.files)));
        self.files.sort();

    def gen_file_tree_out(self):
        print("Log: Get file tree list");
        isFork = lambda fd : fd.endswith("RQ") or fd.endswith("RS");
        files = [val[:-4] for val in self.files];
        for fname in files:
            # find rq & rs pair
            if isFork(fname):
                fname = fname[:-2];
                # add as pair
                pair_index = [i for i,s in enumerate(files) if s.find(fname) != -1];
                if len(pair_index) == 2:
                    # append pair to tree
                    [self.file_tree.append(("{}/{}".format(self.path_out, fname), "{}.cs".format(files[i]))) for i in pair_index];
                    # remove latest files list
                    files.pop(max(pair_index));
                    continue;
            # add to common file[fname]
            self.file_tree.append(("{}".format(self.path_out), "{}.cs".format(fname)));

    def create_tree_dir(self):
        print("Log: Create otput file tree");
        # remove last output & create new
        if os.path.isdir(self.path_out):
            shutil.rmtree(self.path_out);
            if os.path.exists(self.path_out):
                os.makedirs(self.path_out);
        # create dir tree
        for path in self.file_tree:
            if not os.path.exists(path[0]): os.makedirs(path[0]);

    def is_tree_dir_exists(self):
        if os.path.exists(self.path_out):
            return len([pair for pair in self.file_tree if os.path.exists("{0}/{1}".format(pair[0],pair[1]))]) == len(self.file_tree);
        return False;

    # TODO: сделать обработку по stage
    def run(self):
        # Check avability
        #self.check_xsd_available();
        # Print dialog
        self.print_dialog();
        # Get files and check 
        self.get_files();
        # get output file tree
        self.gen_file_tree_out();
        # check folder
        if  self.is_tree_dir_exists():
            over_dial = input("Folder with three structure exists, overwrite? (y/n)? : default: 'n' ");
            if over_dial.lower() == 'y':
                self.process_all();
            else:
                #TODO: Analyze files
                self.analyzer.run();
        else:
            self.process_all();
            #TODO: Analyze files
            self.analyzer.run();

    def process_all(self):
        # create directories
        self.create_tree_dir();
        # process files
        l = len(self.files);
        for i in range(l):
            try:
                self.process_one(self.files[i], self.file_tree[i]);
                print("Proceded :[{} in {}] => filename: {}; Status: OK".format(i, l, self.files[i]));
            except Exception as e:
                print("Error : {0}".format(e.args[0]));
                exit(-1);

    # processing files on cmd util
    def process_one(self, src, dest_pair):
        code = subprocess.call(self.cmd.format(src, self.namespace + "." + dest_pair[0].replace('/', '.'), dest_pair[1]), creationflags=0x08000000); # CREATE_NO_WINDOW
        if code == 0:
            os.rename(dest_pair[1], "{}/{}".format(dest_pair[0], dest_pair[1]));
        else:
            raise Exception("process code != 0");     

    def check_xsd_available(self):
        try:
            if not os.popen("where " + self.modes[self.mode]).read():
                raise FileNotFoundError;
        except FileNotFoundError:
            print("Error: Specify {} as Path variable!".format(self.modes[self.mode]));
            exit(-1);

# Analyze and remove duplicate classes in file
class Analyze:
    def __init__(self, file_tree):
        self.common_filename = "CommonTypes.cs";
        self.file_tree = file_tree;
        self.common_filename_data = None;
        self.parser = Parser();
        
    def run(self):
        print("Log: run analyze");
        try:
            self.process_common_file();
        except Exception as e:
                print("Error : {0}".format(e.args[0]));
                return;
            
    def process_common_file(self):
        comm_file = self.parser.get_common_map;
        if comm_file != None:
            return;
        print("Log: process common file");
        path = ["{0}/{1}".format(pair[0], pair[1]) for pair in self.file_tree if pair[1] == self.common_filename];
        path = str(path[0]);
        if not os.path.exists(path):
            raise Exception("{0} not found! Analyze stoped!".format(path));        
        file_content = open(path, 'r').read();
        print(file_content)
        exit(-1)
        
        # parse file
        comm_file = self.parser.parse_file(file_content, True);


# C# simplify parser
import re

class Parser:    
    def __init__(self):
        self.regex_class_begin = r"class\s+([a-zA-Z]+)\s+{";
        self.regex_atribute = r"\[[\w|\.|(|,|\"|)|=|\s]+]";
        self.common_map_content = None;

    @property
    def get_common_map(self):
        return self.common_map_content;

    # Позволяет парсить классы из cs файлов
    # для общего файла фозвращяет map<file, hash>
    # для других map<file, (start_pos, end_pos)>
    def parse_file(self, content, is_common_file):
        print("Log: parse {} file".format("common" if is_common_file else "class"));
        pattern_class_begin = re.compile(self.regex_class_begin);
        pattern_attribute = re.compile(self.regex_atribute);
        map_file = dict();
        is_atttribute = lambda s : pattern_attribute.search(s) != None;
        for i in range(len(content)):
            match = pattern_class_begin.search(content[i])
            if match != None:
                start = i;
                #find class end
                open_braces = 1;
                while(open_braces != 0):
                    i += 1;
                    st = content[i];
                    if st.find('{') != -1:
                        open_braces += 1;
                    if st.find('}') != -1:
                        open_braces -= 1;
                end = i;
                # find attributes
                back_ind = start - 1;
                while( True ):
                    if is_atttribute( content[back_ind] ):
                        back_ind -= 1;
                        continue;
                    break;
                start = start if back_ind == start - 1 else back_ind + 1;
                # add to map
                if is_common_file:
                    #print ("Class was found at {0}-{1}: name: {class_name}".format( start, end, class_name = match.groups()[0]))
                    map_file[match.groups()[0]] = hash(str(content[start : end]));
                else:
                    map_file[match.groups()[0]] = (start, end);
        print("Found: {} classes".format(len(map_file)));
        return map_file;      


# run app
if __name__ == "__main__":
    if not os.name == "nt":
        print ("Sorry, only Windows ;(");
    else:
        gen = Generator();
        gen.run();
        print("Done!");
