import xaeian as xn, utils
import os, sys, argparse
from datetime import datetime

xn.FIX_PATH = True

parser = argparse.ArgumentParser(description="PySync")
parser.add_argument("-u", "--update", action="store_true", help="Update libraries to latest version (most recently modified)")
parser.add_argument("-e", "--example", action="store_true", help="Create example configuration files 'dict.ini' and 'sync.ini'")
parser.add_argument("-v", "--version", action="store_true", help="Wersję programu 'wizard' oraz inne informacje")
args = parser.parse_args()

if args.version:
  # 1.0.0: Init + (whiteList & blackList)
  print(f"LipySync {xn.Color.BLUE}1.0.0{xn.Color.END}")
  print(f"Repo: {xn.Color.GREY}https://{xn.Color.END}github.com/{xn.Color.TEAL}Xaeian{xn.Color.END}/LipySync")
  sys.exit(0)

if args.example:
  import example
  example.Create()
  sys.exit(0)

sync = xn.JSON.Load("sync.json")
if not sync:
  print(f"{xn.Ico.ERR} Missing file or invalid config file {xn.Color.RED}sync.json{xn.Color.END}")
  sys.exit(0)
mydict = xn.INI.Load("dict.ini")
if not sync:
  print(f"{xn.Ico.ERR} Missing file or invalid config file {xn.Color.RED}dict.json{xn.Color.END}")
  sys.exit(0)

reversed_mydict = {value: key for key, value in mydict.items()}
sync = xn.ReplaceMap(sync, mydict, "{", "}")
for sy in sync:
  sy["paths"] = xn.ReplaceMap(sy["paths"], { "name": sy["name"] }, "{", "}")

name_set, path_set = set(), set()

# Validation to ensure names & paths are unique
for sy in sync:
  if sy["name"] in name_set:
    print(f"{xn.Ico.ERR} Synchronized library name {xn.Color.RED}{sy["name"]}{xn.Color.END} is duplicated")
    sys.exit(0)
  name_set.add(sy["name"])
  for path in sy["paths"]:
    if path.startswith("#"):
      sy["paths"].remove(path)
      continue
    if path in path_set:
      print(f"{xn.Ico.ERR} Path name {xn.Color.RED}{path}{xn.Color.END} appears multiple times")
      sys.exit(0)
    path_set.add(path)

update_flag = False

def SyncFile(name:str, paths:list[str]):
  global update_flag
  paths = [xn.FixPath(path) for path in paths]
  missing = [file for file in paths if not os.path.isfile(file)]
  if missing:
    print(f"{xn.Ico.ERR} Missing {xn.Color.RED}{name}{xn.Color.END} file: {xn.Color.ORANGE}{missing[0]}{xn.Color.END}")
    sys.exit(0)
  hashs = [utils.HashFile(path) for path in paths]
  update_stamps = [os.path.getmtime(path) for path in paths]
  create_stamps = [os.path.getctime(path) for path in paths]
  dts = [datetime.fromtimestamp(stamp).strftime('%Y-%m-%d %H:%M:%S') for stamp in update_stamps]
  if xn.isUniform(hashs): return
  stamp_max = max(update_stamps)
  id = update_stamps.index(stamp_max)
  lats_hash = hashs[id]
  lats_file = paths[id]
  lats_dt = dts[id]
  print(f"{xn.Ico.DOC} Latest {xn.Color.BLUE}{name}{xn.Color.END} file: {xn.Color.GREY}{lats_file}{xn.Color.END} ({xn.Color.TEAL}{lats_dt}{xn.Color.END})")
  for file, hash, dt, ustamp, cstamp in zip(paths, hashs, dts, update_stamps, create_stamps):
    if hash != lats_hash:
      update_flag = True
      if args.update:
        backup_name = xn.ReplaceMap(file, reversed_mydict).replace("/", utils.SEP).replace("\\", utils.SEP)
        utils.BackupFile(file, backup_name)
        if utils.OverwriteFile(lats_file, file):
          print(f"{xn.Ico.OK} File {xn.Color.GREY}{file}{xn.Color.END} update {xn.Color.GREEN}OK{xn.Color.END}")
        else:
          print(f"{xn.Ico.ERR} File {xn.Color.GREY}{file}{xn.Color.END} update {xn.Color.RED}failed{xn.Color.END}")
      else:
        print(f"{xn.Ico.WRN} File {xn.Color.GREY}{file}{xn.Color.END} needs update ({xn.Color.TEAL}{dt}{xn.Color.END})")
        if ustamp == cstamp:
          print(f"{xn.Ico.ERR} But it was created recently, make sure it's not actually newer!")
    elif args.update and file !=lats_file:
      print(f"{xn.Ico.OK} File {xn.Color.GREY}{file}{xn.Color.END} is up-to-date")

def SyncFolder(name:str, paths:list[str], whitelist:list[str]|None=None, blacklist:list[str]=[]):
  files = [utils.FileList(path) for path in paths]
  if whitelist: files.append(whitelist)
  files = utils.IntersectionList(files)
  files = [file for file in files if file not in blacklist]
  for file in files:
    files_path = [f"{path}/{file}" for path in paths]
    SyncFile(f"{name}/{file}", files_path)

for sy in sync:
  whitelist = sy.get("whiteList", None)
  blacklist = sy.get("blackList", [])
  if sy.get("file", True): SyncFile(sy["name"], sy["paths"])
  else: SyncFolder(sy["name"], sy["paths"], whitelist, blacklist)

if not update_flag:
  print(f"{xn.Ico.YEA} All files are in the same version {xn.Color.GREY}(no update is needed){xn.Color.END}")
elif not args.update:
  print(f"{xn.Ico.INF} To update older files, run script with flag {xn.Color.YELLOW}-u{xn.Color.END} {xn.Color.GREY}--update{xn.Color.END}")
