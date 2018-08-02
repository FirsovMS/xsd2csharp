xsd2csharp
=========
Simple script to convert  *.xsd files to c# service classes.
The converter groups your classes in separate folders by name.

Files that have a difference in the name based on the characteristics
"RQ" or "RS", Will be moved to a folder that is based on a name without this specification.

Using
-----
1) Add your xsd.exe tool to Path variable on your system.
2) Run `python convert.py` in folder with XSD files.
3) Wait, process is finish.
4) Go to `out` folder, that contained your new classes.
