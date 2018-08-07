#!/usr/bin/python

import os
import shutil
import subprocess
import re

from classes.generator import Generator
from classes.analyze import Analyze
from classes.parser import Parser

__DIR__ = os.path.curdir;

__xsd_path__ = __DIR__ + "./xsd2code/Xsd2Code.exe";

if __name__ == "__main__":
    try:
        if not os.path.exists(__xsd_path__) :
            raise FileNotFoundError("xsd2Code didn't exists! Check folder 'xsd2code' in current dir!")

        generator = Generator();
        
        generator.run();

        
    except Exception as e:
        print("Error message: " + e.args[0]);
        exit(-1);
    print("Done!");
