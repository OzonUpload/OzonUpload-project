import os
import sys

libs_path = "Libs"
OzonSeller_libs = [files for files in os.listdir(libs_path) if files.startswith("OzonSeller")][-1]
parser_libs = [files for files in os.listdir(libs_path) if files.startswith("parser")][-1]
MyFunc_libs = [files for files in os.listdir(libs_path) if files.startswith("MyFunc")][-1]

match sys.argv[1]:
    case "libs":
        os.system(f"pip install Libs/{OzonSeller_libs} Libs/{parser_libs} Libs/{MyFunc_libs}")
    case "ozon_seller":
        os.system(f"pip install Libs/{OzonSeller_libs}")
    case "parser":
        os.system(f"pip install Libs/{parser_libs}")
    case "MyFunc":
        os.system(f"pip install Libs/{MyFunc_libs}")
    case "full":
        os.system(f"pip install Libs/{OzonSeller_libs} Libs/{parser_libs} Libs/{MyFunc_libs}")
        if os.path.exists("requiments.txt"):
            os.system("pip install -r requiments.txt")
