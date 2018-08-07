
# Analyze and remove duplicate classes in file
class Analyze:
    def __init__(self, file_tree, head_node):
        self.common_filename = head_node;
        ##  [(filename, path)...]
        self.file_tree = file_tree;
        self.parser = Parser();
        self.common_maps = None;
        
    def run(self):
        print("Log: run analyze");
        try:
            pair = [(i, pair) for i, pair in enumerate(self.file_tree) if pair[1] == self.common_filename]
            ind = int(pair[0][0]);
            path = "{0}/{1}".format(pair[0][1][0], pair[0][1][1]);
            # process common file
            self.process_file(self.common_filename, path)
            # remove recent
            self.file_tree.pop(ind);
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
