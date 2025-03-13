import pathlib, hashlib, shutil
from datetime import datetime
import xaeian as xn

SEP = "@"

def HashFile(path:str):
  hasher = hashlib.md5()
  with open(path, "rb") as file:
    buf = file.read()
    hasher.update(buf)
  return hasher.hexdigest()

def OverwriteFile(src:str, dsc:str):
  try:
    shutil.copyfile(src, dsc)
    return True
  except FileNotFoundError: return False
  except Exception as e: return False

def BackupFile(src:str, name:str, backup_path:str="./backups"):
  backup_path = xn.FixPath(backup_path)
  path = f"{backup_path}/{datetime.now().strftime(f"%Y-%m-%d{SEP}%H-%M-%S")}"
  pathlib.Path(path).mkdir(parents=True, exist_ok=True)
  shutil.copyfile(src, f"{path}/{name}")

def FileList(path:str):
  folder_path = pathlib.Path(path)
  return [file.name for file in folder_path.iterdir() if file.is_file()]

def IntersectionList(lists: list[list]) -> set:
  if not lists:
    return []
  return list(set(lists[0]).intersection(*lists[1:]))
