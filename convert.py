#!/usr/bin/python

import os
import subprocess
import shutil

class Generator:
    def __init__(self):
        self.path_in = ".";
        self.path_out = "./out";
        self.modes = ["Xsd2Code", "wsdl"];
        self.mode = 0;
        self.namespace = "TravelSkyDLL.Lib.XML";
        self.files = [];

    def print_dialog(self):
        print("Modes available:");
        for k in range(len(self.modes)):
            print(k,".",self.modes[k]);
        m = input("Pick mode number! (defalut {}): ".format(self.mode));
        m = int(m) if m else 0;
        self.mode = m if m >= 0 and m < len(self.modes) else 0;
        print("Choosed mode: {}".format(self.modes[self.mode]));
        base = input("Enter base namespace: (example and default :'{}'): ".format(self.namespace));
        if base: self.namespace = base;
        # add namespace folder based on current folder name
        self.path_out = os.getcwd().split("\\")[-1].split('.')[0];
        self.namespace += "." + self.path_out;

    def run(self):
        self.print_dialog();
        self.check_xsd_available();
        # fill files list
        for file in os.listdir(self.path_in):
            if file.endswith(".xsd"): self.files.append(file);
        length = len(self.files);
        if length == 0: exit(0);
        self.rm_dir();
        ind = 1;
        CREATE_NO_WINDOW = 0x08000000;
        # create base out dir
        if not os.path.exists(self.path_out): os.makedirs(self.path_out);
        # run method
        isFork = lambda fd : fd.endswith("RQ") or fd.endswith("RS");
        for f in self.files:
            out_dir = self.is_existed_dir(f);
            namespace = self.namespace if not isFork(f.strip()[:-4]) else self.namespace + "." + out_dir.split('/')[-1];
            out_fname = f[:-4] + ".cs";            
            cmd = "Xsd2Code {} {} {} -o -platform Net35".format(f, namespace, out_fname) if self.mode == 0 else "xsd {} -classes".format(f);
            try:
                code = subprocess.call(cmd, creationflags=CREATE_NO_WINDOW);
                # move to folder
                if code == 0: os.rename("./" + out_fname, out_dir + "/" + out_fname);
            except OSError:
                print ("Error: popen");
            code = "OK" if code == 0 else "Bad";
            # print message
            print("Proceded :[{} in {}] => filename: {}; Status: {}".format(ind, length, f, code));
            ind +=1;

    def rm_dir(self):
        if os.path.isdir(self.path_out): shutil.rmtree(self.path_out);

    def is_existed_dir(self, file):
        file = file.strip()[:-4];
        if file.endswith("RQ") or file.endswith("RS"):
            newpath = self.path_out + "/";
            newpath += file[:-2] if file.endswith("RQ") or file.endswith("RS") else file;
            if not os.path.exists(newpath): os.makedirs(newpath);
            return newpath;
        return self.path_out;

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
