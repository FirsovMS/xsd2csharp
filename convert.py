#!/usr/bin/python

import os
import subprocess
import shutil
import re

# Simple csharp clsses parser
class Parser:    
    def __init__(self):
        self.regex_class_begin = r"class\s+([a-zA-Z]+)\s+{";
        self.regex_atribute = r"\[[\w|\.|(|,|\"|)|=|\s]+]";

    # Позволяет парсить классы из cs файлов
    # для общего файла фозвращяет map<file, hash>
    # для других [file, (start_pos, end_pos)]
    def parse_file(self, content, is_common_file):
        print("Log: parse {} file".format("common" if is_common_file else "class"));
        pattern_class_begin = re.compile(self.regex_class_begin);
        map_file = dict() if is_common_file else list();
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
##                back_ind = start - 1;
##                while( True ):
##                    if is_atttribute( content[back_ind] ):
##                        back_ind -= 1;
##                        continue;
##                    break;
##                start = start if back_ind == start - 1 else back_ind + 1;
                # add to map
                if is_common_file:
                    #print ("Class was found at {0}-{1}: name: {class_name}".format( start, end, class_name = match.groups()[0]))
                    map_file[match.groups()[0]] = hash(str(content[start : end]));
                else:
                    map_file.append( ( (match.groups()[0], hash(str(content[start : end]))) , (start, end)) );
        print("Found: {} classes".format(len(map_file)));
        return map_file;

    # return back start, end position
    def find_position_with_attribute(self, content, start, end):
##        pattern_attribute = re.compile(self.regex_atribute);
##        is_atttribute = lambda s : pattern_attribute.search(s) != None;
        is_atttribute = lambda s : s.find('[') != -1 and s.find(']') != -1;
        back_ind = start - 1;
        while( True ):
            if is_atttribute( content[back_ind] ):
                back_ind -= 1;
                continue;
            break;
        start = start if back_ind == start - 1 else back_ind + 1;
        return start, end;

# Analyze and remove duplicate classes in file
class Analyze:
    def __init__(self, file_tree):
        self.common_filename = "CommonTypes.cs";
        ##  [(filename, path)...]
        self.file_tree = file_tree;
        self.parser = Parser();
        self.common_maps = None;
        
    def run(self):
        print("Log: run analyze");
        try:
            path = ["{0}/{1}".format(pair[0], pair[1]) for pair in self.file_tree if pair[1] == self.common_filename];
            path = str(path[0]);
            # process common file
            self.process_file(self.common_filename, path)
            # process others
            for pair in self.file_tree:
                    path = "{0}/{1}".format(pair[0], pair[1]);
                    self.process_file(pair[1], path);            
        except Exception as e:
            raise e;
            print("Error : {0}".format(e.args[0]));
            return;

    def load_file(self, path):
        fd = open(path, 'r');
        cont = fd.readlines()
        fd.close();
        return cont;

    def write_file(self, content, path):
        print("Log: write file to : " + path);
        fd = open(path, 'w');
        [fd.write(str_) for str_ in content]
        fd.close();

    def process_file(self, filename, full_path):
        if not os.path.exists(full_path):
            raise Exception("{0} not found! Analyze stoped!".format(path));  
        file_content = self.load_file(full_path);
        if filename == self.common_filename:
            if self.common_maps == None:
                print("Log: process common file: " + self.common_filename);
                # get map<fname, hash>
                self.common_maps = self.parser.parse_file(file_content, True);
        else:
            print("Log: process file " + filename);
            # get map<fname, (start, end)>
            file_map = self.parser.parse_file(file_content, False);
            clear_class = self.remove_enites(file_map, file_content);
            # write file
            self.write_file(clear_class, full_path);

    # return <str> of *.cs file without class duplicate on file_map
    def remove_enites(self, file_map, file_content):
        print("Log: remove duplicate classes");
        content = file_content[:]
        for class_data, class_pos in file_map:
            try:
                # compare hashes
                if self.common_maps[class_data[0]] == class_data[1]:
                    # get class ranges with attributes
                    start, end = self.parser.find_position_with_attribute(content, class_pos[0], class_pos[1])
##                    print ("Old: [{} : {}]   New: [{} : {}]]".format(class_pos[0], class_pos[1], start , end));
                    # remove class element
                    for i in range(end, start - 1, -1):
                        content.pop(i);
                        content.insert(i, "\n");
            except KeyError:
                continue;
        # remove new lines
        ind_to_remove = [i for i, str_ in enumerate(content) if str_ == "\n"]
        ind_to_remove.sort(reverse = True)
        [content.pop(ind) for ind in ind_to_remove]
        return content;
    

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


# run app
if __name__ == "__main__":
    if not os.name == "nt":
        print ("Sorry, only Windows ;(");
    else:
        gen = Generator();
        gen.run();
        print("Done!");
