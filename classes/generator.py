
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
##        self.analyzer = Analyze(self.file_tree, "CommonTypes.cs");                                                  #!!!

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
        print(self.file_tree)
        exit(0)
        # check folder
        if  self.is_tree_dir_exists():
            over_dial = input("Folder with three structure exists, overwrite? (y/n)? : default: 'n' ");
            if over_dial.lower() == 'y':
                self.process_all();
        else:
            self.process_all();
        #TODO: Analyze files
##        self.analyzer.run();
        analyzer = Analyze(self.file_tree, "CommonTypes.cs");
        analyzer.run()
        for pair in self.file_tree:
            analyzer = Analyze(self.file_tree, pair[1]);
            analyzer.run()

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
                print("Error : Can't generate files! Code: {0}".format(e.args[0]));
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
