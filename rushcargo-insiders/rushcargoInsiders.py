import subprocess

# Path to the Python Interpreter that runs any Python Script under the Virtual Environment
pythonBin = "./venv/Scripts/python.exe"

# Path to the Python Script that must run under the Virtual Environment
scriptFile = "./src/main.py"

try:
    subprocess.Popen([pythonBin, scriptFile])
except Exception as err:
    print(err)
    input("Press ENTER to Exit")
