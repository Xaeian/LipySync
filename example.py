import os, platform
import xaeian as xn

user = os.getlogin()
if platform.system() == "Windows": base_path = f"C:/Users/{user}"
else: base_path = f"/home/{user}"

mydict = {
  "web": os.path.join(base_path, "Projects", "WebPage", "backend").replace("\\", "/"),
  "staff": os.path.join(base_path, "Desktop", "MyStaff", "test").replace("\\", "/"),
  "work": os.path.join(base_path, "Work", "Drivers", "repos").replace("\\", "/")
}

sync = [
  {
    "name": "serial_port.c",
    "paths": [
      "{staff}/serial.c",
      "{work}/PLC/{name}"
    ]
  },
  {
    "name": "utils",
    "paths": [
      "{web}/lib/{name}",
      "#{staff}/python/{name}.py",
      "{work}/PLC/misc.py"
    ]
  },
  {
    "name": "protobuf",
    "paths": [
      "{web}/proto/",
      "{staff}/{name}/"
    ]
  }
]

def Create():
  mydict_file = "dict.ini"
  if os.path.exists(mydict_file):
    print(f"{xn.Ico.ERR} File {xn.Color.RED}{mydict_file}{xn.Color.END} already exists. Delete it to generate the example")
  else:
    print(f"{xn.Ico.OK} Template file {xn.Color.GREEN}{mydict_file}{xn.Color.END} has been generated")
    xn.INI.Save(mydict_file, mydict)
  sync_file = "sync.json"
  if os.path.exists(sync_file):
    print(f"{xn.Ico.ERR} File {xn.Color.RED}{sync_file}{xn.Color.END} already exists. Delete it to generate the example")
  else: 
    print(f"{xn.Ico.OK} Template file {xn.Color.GREEN}{sync_file}{xn.Color.END} has been generated")
    xn.JSON.SavePretty(sync_file, sync)
