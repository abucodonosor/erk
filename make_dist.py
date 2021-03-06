
import os
import sys
import shutil

f = open("./erk/data/minor.txt","r")
mversion = f.read()
f.close()

mversion = int(mversion)+1
mversion = str(mversion)

f = open("./erk/data/minor.txt","w")
f.write(mversion)
f.close()

from erk.strings import *

# Build distribution zips

os.mkdir("./dist")
os.mkdir("./dist/settings")

os.mkdir("./dist/plugins")
os.mkdir("./dist/plugins/examples")

shutil.copy("./plugins/examples/hello.png", "./dist/plugins/examples/hello.png")
shutil.copy("./plugins/examples/notes.png", "./dist/plugins/examples/notes.png")
shutil.copy("./plugins/examples/hello.py", "./dist/plugins/examples/hello.py")
shutil.copy("./plugins/examples/notes.py", "./dist/plugins/examples/notes.py")
shutil.copy("./plugins/examples/package.png", "./dist/plugins/examples/package.png")
shutil.copy("./plugins/examples/package.txt", "./dist/plugins/examples/package.txt")

os.mkdir("./dist/documentation")
shutil.copy("./documentation/Erk_Plugin_Guide.pdf", "./dist/documentation/Erk_Plugin_Guide.pdf")

os.mkdir("./dist/macros")
shutil.copy("./macros/trout.json", "./dist/macros/trout.json")

os.system("compile_resources.bat")

shutil.copytree("./erk", "./dist/erk",ignore=shutil.ignore_patterns('*.pyc', 'tmp*',"__pycache__"))

shutil.copytree("./spellchecker", "./dist/spellchecker",ignore=shutil.ignore_patterns('*.pyc', 'tmp*',"__pycache__"))
shutil.copytree("./emoji", "./dist/emoji",ignore=shutil.ignore_patterns('*.pyc', 'tmp*',"__pycache__"))

shutil.copy("./erk.py", "./dist/erk.py")

shutil.copy("./LICENSE", "./dist/LICENSE")

os.system("powershell.exe -nologo -noprofile -command \"& { Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::CreateFromDirectory('dist', 'erk_dist.zip'); }\" ")

shutil.rmtree('./dist')

archive_name = f"{NORMAL_APPLICATION_NAME.lower()}-{APPLICATION_MAJOR_VERSION}.zip"

os.rename('erk_dist.zip', archive_name)

os.remove(f"./downloads/{archive_name}")
os.remove("./downloads/erk-latest.zip")

shutil.copy(archive_name, "./downloads/"+archive_name)
shutil.copy(archive_name, "./downloads/erk-latest.zip")

os.remove(archive_name)
