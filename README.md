# csv2dd

Generate dynamicData objects in FreeCAD from csv file.

[YOUTUBE VIDEO](https://www.youtube.com/watch?v=rwHM5EOdgpU&t=7s)

## Usage
1. Execute the macro
2. Indicate the path for csv file. The file must contain the same structure as csvFile.csv in this repository. First row is ignorated. If csv2dd.txt file exists in same macro path containing csv path, then it is used withouth asking.
3. If dynamicData object exists in the FreeCAD file with de same name as indicated in csv file, it is updated and not duplicated.
4. If all is fine, the macro pops up a message.
