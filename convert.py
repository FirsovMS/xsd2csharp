#!/usr/bin/python

import os
import subprocess

class Generator:
    def __init__(self):
        self.path_in = ".";
        self.path_out = "./out";
        self.files = [];

    def run(self):
        self.check_xsd_available();
        for file in os.listdir(self.path_in):
            if file.endswith(".xsd"): self.files.append(file);
        length = len(self.files);
        ind = 1;
        CREATE_NO_WINDOW = 0x08000000;
        for f in self.files:
            out_dir = self.is_existed_dir(f);
            cmd = "xsd " + self.path_in + "\\" + f + " -classes -outputdir:" + out_dir;
            try:
                code = subprocess.call(cmd, creationflags=CREATE_NO_WINDOW);
            except OSError:
                print ("Error: popen");
            code = "OK" if code == 0 else "Bad";
            print("Proceded :[{} in {}] => filename: {}; Status: {}".format(ind, length, f, code));
            ind += 1;

    def is_existed_dir(self, file):
        file = file.strip()[:-4];
        newpath = self.path_out + "/";
        newpath += file[:-2] if file.endswith("RQ") or file.endswith("RS") else file; 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        return newpath;

    def check_xsd_available(self):
        try:
            subprocess.call("xsd");
        except FileNotFoundError:
            print("Error: Specify xsd.exe as Path variable!");
            exit(-1);        

gen = Generator();
gen.run();


