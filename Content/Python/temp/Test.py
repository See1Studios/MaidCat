from logging import log
import sys
import unreal

pathList = " \n"
pathList += "------------------------------------------------------------------------------------\n"
pathList += "Unreal Python Path\n"
pathList += "------------------------------------------------------------------------------------\n"
pathList += "\n"

for path in sys.path:
    pathList +="\n"
    pathList +=path
print(pathList)

unreal.log_error("Python Unreal API Error")
unreal.log_warning("Python Unreal API Warning")
unreal.log("Python Unreal API Log")