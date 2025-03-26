import xaeian as xn, utils
import os, sys, argparse
from datetime import datetime

class Ico(xn.IcoText): pass
class Color(xn.Color): pass

xn.FIX_PATH = True

parser = argparse.ArgumentParser(description="PySync")
parser.add_argument("-u", "--update", action="store_true", help="Update libraries to latest version (most recently modified)")
parser.add_argument("-i", "--info", action="store_true", help="Displays a list of all synchronized files (not quiet)")
parser.add_argument("-e", "--example", action="store_true", help="Create example configuration files 'dict.ini' and 'sync.ini'")
parser.add_argument("-v", "--version", action="store_true", help="Program version and repository location")
args = parser.parse_args()

if args.version:
  # 1.2.0: Auto-detect file/folder + info + paths unique lib only
  # 1.1.0: Union files for SyncFolder
  # 1.0.0: Init + (whiteList & blackList)
  print(f"LipySync {Color.BLUE}1.2.0{Color.END}")
  print(f"Repo: {Color.GREY}https://{Color.END}github.com/{Color.TEAL}Xaeian{Color.END}/LipySync")
  sys.exit(0)

if args.example:
  import example
  example.Create()
  sys.exit(0)

sync = xn.JSON.Load("sync.json")
if not sync:
  print(f"{Ico.ERR} Missing file or invalid config file {Color.RED}sync.json{Color.END}")
  sys.exit(0)
mydict = xn.INI.Load("dict.ini")
if not sync:
  print(f"{Ico.ERR} Missing file or invalid config file {Color.RED}dict.json{Color.END}")
  sys.exit(0)

reversed_mydict = {value: key for key, value in mydict.items()}
sync = xn.ReplaceMap(sync, mydict, "{", "}")
for sy in sync:
  sy["paths"] = xn.ReplaceMap(sy["paths"], { "name": sy["name"] }, "{", "}")

# Validation to ensure names & paths are unique
name_set = set()
for sy in sync:
  if sy["name"] in name_set:
    print(f"{Ico.ERR} Synchronized library name {Color.RED}{sy["name"]}{Color.END} is duplicated")
    sys.exit(0)
  name_set.add(sy["name"])
  path_set = set()
  cnt_file = 0
  cnt_dir = 0
  for path in sy["paths"]:
    if path.startswith("#"):
      sy["paths"].remove(path)
      continue
    if os.path.isfile(path): cnt_file += 1
    elif os.path.isdir(path): cnt_dir += 1
    else:
      print(f"{Ico.ERR} Path {Color.ORANGE}{path}{Color.END} in library {Color.RED}{sy["name"]}{Color.END} doesn't exist")
    if path in path_set:
      print(f"{Ico.ERR} Path {Color.ORANGE}{path}{Color.END} in library {Color.RED}{sy["name"]}{Color.END} appears multiple times")
      sys.exit(0)
    path_set.add(path)
  if cnt_file and cnt_dir:
    print(f"{Ico.ERR} Library {Color.RED}{sy["name"]}{Color.END} contains files and folders paths")
  sy["file"] = True if cnt_file else False 

update_flag = False

def SyncFile(name:str, paths:list[str], must_exist:bool=True):
  global update_flag
  paths = [xn.FixPath(path) for path in paths]
  if must_exist:
    missing = [file for file in paths if not os.path.isfile(file)]
    if missing:
      print(f"{Ico.ERR} Missing {Color.RED}{name}{Color.END} file: {Color.ORANGE}{missing[0]}{Color.END}")
      sys.exit(0)
  else:
    paths = [file for file in paths if os.path.isfile(file)]
  hashs = [utils.HashFile(path) for path in paths]
  update_stamps = [os.path.getmtime(path) for path in paths]
  create_stamps = [os.path.getctime(path) for path in paths]
  dts = [datetime.fromtimestamp(stamp).strftime('%Y-%m-%d %H:%M:%S') for stamp in update_stamps]
  if xn.isUniform(hashs) and not args.info: return
  stamp_max = max(update_stamps)
  id = update_stamps.index(stamp_max)
  lats_hash = hashs[id]
  lats_file = paths[id]
  lats_dt = dts[id]
  print(f"{Ico.DOC} Latest {Color.BLUE}{name}{Color.END} file: {Color.GREY}{lats_file}{Color.END} ({Color.TEAL}{lats_dt}{Color.END})")
  for file, hash, dt, ustamp, cstamp in zip(paths, hashs, dts, update_stamps, create_stamps):
    if hash != lats_hash:
      update_flag = True
      if args.update:
        backup_name = xn.ReplaceMap(file, reversed_mydict).replace("/", utils.SEP).replace("\\", utils.SEP)
        utils.BackupFile(file, backup_name)
        if utils.OverwriteFile(lats_file, file):
          print(f"{Ico.OK} File {Color.GREY}{file}{Color.END} update {Color.GREEN}OK{Color.END}")
        else:
          print(f"{Ico.ERR} File {Color.GREY}{file}{Color.END} update {Color.RED}failed{Color.END}")
      else:
        print(f"{Ico.WRN} File {Color.GREY}{file}{Color.END} needs update ({Color.TEAL}{dt}{Color.END})")
        if ustamp == cstamp:
          print(f"{Ico.ERR} But it was created recently, make sure it's not actually newer!")
    elif (args.update or args.info) and file != lats_file:
      print(f"{Ico.OK} File {Color.GREY}{file}{Color.END} is up-to-date")

def SyncFolder(name:str, paths:list[str], whitelist:list[str]|None=None, blacklist:list[str]=[]):
  try:
    files = [utils.FileList(path) for path in paths]
  except Exception as e:
    print(f"{Ico.ERR} {e}")
    sys.exit(0)
  files = utils.UnionList(files)
  if whitelist: files = utils.IntersectionList([files] + [whitelist])
  files = [file for file in files if file not in blacklist]
  for file in files:
    files_path = [f"{path}/{file}" for path in paths]
    SyncFile(f"{name}/{file}", files_path, False)

for sy in sync:
  whitelist = sy.get("whiteList", None)
  blacklist = sy.get("blackList", [])
  if sy.get("file", True): SyncFile(sy["name"], sy["paths"])
  else: SyncFolder(sy["name"], sy["paths"], whitelist, blacklist)

if not update_flag:
  print(f"{Ico.YEA} All files are in the same version {Color.GREY}(no update is needed){Color.END}")
elif not args.update:
  print(f"{Ico.INF} To update older files, run script with flag {Color.YELLOW}-u{Color.END} {Color.GREY}--update{Color.END}")
