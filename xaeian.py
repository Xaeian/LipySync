import os, sys, re, csv, json
from typing import Iterable, Any

#------------------------------------------------------------------------------ Files

FIX_PATH = False

def FixPath(path:str):
  path = path.replace("\\", "/")
  if os.path.isabs(path): return path
  path = path.lstrip("./")
  if getattr(sys, 'frozen', False): path = os.path.dirname(sys.executable).replace("\\", "/") + "/" + path
  elif __file__: path = os.path.dirname(__file__).replace("\\", "/") + "/" + path
  return path

class INI:

  @staticmethod
  def Load(path:str, fix:bool|None=None) -> dict:
    path = path.removesuffix('.ini') + '.ini'
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    if not os.path.exists(path):
      return {}
    try:
      with open(path, 'r', encoding="utf-8") as file:
        content = file.read()
    except Exception:
      return {}
    content = re.sub(r"(;|#).*", "", content)
    content = re.sub(r"( *\r?\n *)+", "\n", content)
    lines = content.split("\n")
    ini = {}
    section = None
    for line in lines:
      line = line.strip()
      if not line:
        continue
      if line.startswith("[") and line.endswith("]"):
        section = line[1:-1].strip()
        ini[section] = {}
        continue
      key_value = line.split("=", 1)
      key = key_value[0].strip()
      value = key_value[1].strip() if len(key_value) > 1 else None
      if value:
        if (value[0] == value[-1]) and value[0] in ('"', "'"):
          value = value[1:-1]
        elif value.lower() == "true":
          value = True
        elif value.lower() == "false":
          value = False
        elif not value.startswith("+"):
          try:
            value = int(value, base=0)
          except ValueError:
            try:
              value = float(value)
            except ValueError:
              pass
      if section:
        ini[section][key] = value
      else:
        ini[key] = value
    return ini
  
  @staticmethod
  def Save(path:str, data:dict, fix:bool|None=None):
    path = path.removesuffix(".ini") + ".ini"
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    try:
      with open(path, "w", encoding="utf-8") as file:
        for key, value in data.items():
          if isinstance(value, dict): # Section
            file.write(f"[{key}]\n")
            for sub_key, sub_value in value.items():
              if sub_value is None:
                file.write(f"{sub_key} =\n")
              elif isinstance(sub_value, str):
                file.write(f"{sub_key} = \"{sub_value}\"\n")
              elif isinstance(sub_value, (int, float)):
                file.write(f"{sub_key} = {sub_value}\n")
              else:
                raise ValueError(f"Unsupported value type for key '{sub_key}': {type(sub_value).__name__}")
          else: # Key-value pair outside any section
            if value is None:
              file.write(f"{key} =\n")
            elif isinstance(value, str):
              file.write(f"{key} = \"{value}\"\n")
            elif isinstance(value, (int, float)):
              file.write(f"{key} = {value}\n")
            else:
              raise ValueError(f"Unsupported value type for key '{key}': {type(value).__name__}")
    except Exception as e:
      print(f"Error saving INI file '{path}': {e}")

class CSV:

  @staticmethod
  def Load(path:str, delimiter:str=",", types:dict=None, fix:bool|None=None) -> list:
    path = path.removesuffix(".csv") + ".csv"
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    if not os.path.exists(path):
      return []
    try:
      with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        rows = []
        for row in reader:
          if types:
            for col, ctype in types.items():
              if col in row and row[col] not in (None, ""):
                try:
                  if ctype == int: row[col] = ctype(row[col], base=0)
                  else: row[col] = ctype(row[col])
                except (ValueError, TypeError):
                  print(f"Warning: Could not convert value '{row[col]}' in column '{col}' to {ctype.__name__}.")
                  row[col] = None
          rows.append(row)
        return rows
    except Exception as e:
      print(f"Error loading file '{path}': {e}")
      return []

  @staticmethod
  def AddRow(path:str, datarow:dict|list=[], fix:bool|None=None):
    path = path.removesuffix(".csv") + ".csv"
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as csv_file:
      if isinstance(datarow, dict):
        field_names = list(datarow.keys())
        writer = csv.DictWriter(csv_file, field_names=field_names)
        if not file_exists:
          writer.writeheader()
        writer.writerow(datarow)
      elif isinstance(datarow, list):
        writer = csv.writer(csv_file)
        writer.writerow(datarow)
      else:
        raise ValueError("Variable 'datarow' must be a dictionary or a list")

  @staticmethod
  def Save(path:str,data:list[dict]|list[list],field_names:list=None, fix:bool|None=None):
    path = path.removesuffix(".csv") + ".csv"
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
      if all(isinstance(row, dict) for row in data):
        field_names = field_names or list(data[0].keys())
        writer = csv.DictWriter(csv_file, field_names=field_names)
        writer.writeheader()
        writer.writerows(data)
      elif all(isinstance(row, list) for row in data):
        if not field_names:
          raise ValueError("Field names must be provided when saving lists")
        writer = csv.writer(csv_file)
        writer.writerow(field_names)
        writer.writerows(data)
      else:
        raise ValueError("Data must be a list of dictionaries or lists")

class JSON:

  @staticmethod
  def Load(path:str, otherwise: None|list|dict=None, fix:bool|None=None) -> dict|list|None:
    path = path.removesuffix(".json") + ".json"
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    if not os.path.isfile(path):
      return otherwise
    try:
      with open(path, "r", encoding="utf-8") as file:
        content = file.read()
        return json.loads(content) if content else otherwise
    except (json.JSONDecodeError, OSError) as e:
      print(f"Error loading JSON file '{path}': {e}")
      return otherwise

  @staticmethod
  def Save(path:str, content:dict|list|Any, fix:bool|None=None):
    path = path.removesuffix(".json") + ".json"
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    try:
      with open(path, "w", encoding="utf-8") as file:
        json.dump(content, file, separators=(",", ":"))
    except (TypeError, OSError) as e:
      print(f"Error saving JSON file '{path}': {e}")

  @staticmethod
  def SavePretty(path:str, content:dict|list|Any, fix:bool|None=None):
    path = path.removesuffix(".json") + ".json"
    if fix is None: fix = FIX_PATH
    if fix: path = FixPath(path)
    try:
      with open(path, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=2, ensure_ascii=False)
    except (TypeError, OSError) as e:
      print(f"Error saving JSON file '{path}': {e}")

#------------------------------------------------------------------------------ Str

def SplitStr(string:str, split:str= " ", string_char:str='"', escape_char:str = "\\") -> list:
  def trim(value:str) -> str:
    if value[0] == string_char and value[-1] == string_char: return value[1:-1]
    else: return value
  array:list = []
  k:int = 0
  mute:bool = False
  mute_start:bool = False
  mute_end:bool = False
  escape:bool = False
  inc:int = 0
  count:int = len(split)
  val:str = ""
  i:int = 0
  while i < len(string):
    if string[i] == string_char:
      if not mute:
        mute_start = True
        mute = True
        if mute_end == True:
          array.append(trim(val))
          val = ""
    mute_end = False
    if not mute:
      j = 0
      go_continue = False
      while j < count:
        if string[i + j] == split[j]:
          if j + 1 == count:
            if not inc: val = trim(val)
            inc = 0
            k += 1
            array.append(val)
            val = ""
            i += j
            go_continue = True
            break # continue 2
        else:
          break
        j += 1
      if go_continue:
        i += 1
        continue
      inc += 1      
    if mute and not mute_start:
      if string[i] == escape_char: escape = True
      elif not escape and string[i] == string_char:
        mute = False
        mute_end = True
      else: escape = False
    if not escape:
      val += string[i]
    mute_start = False
    if i + 1 == len(string) and not inc:
      val = trim(val)
    i += 1
  array.append(val)
  return array

# test = 'Hello "world" this "\\"" is """ a" "test string" with "escape\\"s: " char'
# result = split_str(test)
# print(result)

def SplitSQL(sqls):
  sqls = SplitStr(sqls, ";", "'")
  for i, sql in enumerate(sqls):
    sql = re.sub(r"[\n\r]+", "", sql)
    sql = re.sub(r"[\ ]+", " ", sql)
    sql = re.sub(r"\ ?\(\ ?", "(", sql)
    sql = re.sub(r"\ ?\)\ ?", ")", sql)
    sql = re.sub(r"\ ?\,\ ?", ",", sql)
    sql = re.sub(r"\ ?\=\ ?", "=", sql)
    sqls[i] = sql
  output = []
  i = 0
  for sql in sqls:
    if sql and sql != " ":
      output.append(sql + ";")
      i += 1
  return output

def ReplaceMap(subject:str|list|dict, mapping:dict, prefix:str="", suffix:str=""):
  # Replace keys in the format prefix + key + suffix with values from the dictionary
  if isinstance(subject, str):
    for search, replace in mapping.items():
        subject = subject.replace(f"{prefix}{search}{suffix}", str(replace))
    return subject
  elif isinstance(subject, list):
    return [ReplaceMap(item, mapping, prefix, suffix) for item in subject]
  elif isinstance(subject, dict):
    return {key: ReplaceMap(value, mapping, prefix, suffix) for key, value in subject.items()}
  else:
    return subject

def isUniform(lst:Iterable):
  return len(set(lst)) == 1

#------------------------------------------------------------------------------ Time

import calendar
from datetime import datetime, timedelta
import pytz, tzlocal

class TIME(datetime):

  def Interval(interval:str="", dt:None|datetime=None):
    dt = TIME.now() if dt is None else dt
    value = re.findall(r"\-?[0-9]*\.?[0-9]+", interval)
    if not value: return dt
    value = float(value[0])
    factor = re.sub("[^a-z]", "", interval.lower())
    if factor == "y" or factor == "mo":
      if factor == "y": value *= 12
      month = dt.month - 1 + int(value)
      year = dt.year + month // 12
      month = month % 12 + 1
      day = min(dt.day, calendar.monthrange(year, month)[1])
      return dt.replace(year, month, day)
    match factor:
      case "w":dt += timedelta(weeks=value)
      case "d":dt += timedelta(days=value)
      case "h":dt += timedelta(hours=value)
      case "m":dt += timedelta(minutes=value)
      case "s":dt += timedelta(seconds=value)
      case "ms":dt += timedelta(milliseconds=value)
      case "us":dt += timedelta(microseconds=value)
    return dt

  def Intervals(intervals:str=""):
    dt = TIME.now()
    for interval in intervals.split():
      dt = TIME.Interval(interval, dt)
    return dt

  def isInterval(text:str):
    if re.search(r"^(\-|\+)?[0-9]*\.?[0-9]+(y|mo|w|d|h|m|s|ms|µs|us)$", text.strip()): return True
    else: return False

  def isIntervals(text:str):
    if re.search(r"^((\-|\+)?[0-9]*\.?[0-9]+(y|mo|w|d|h|m|s|ms|µs|us) ?)*$", text.strip()): return True
    else: return False

  def Create(some:str|int|float|datetime|None="now"):
    if some is None: return None
    if type(some) is datetime: return some
    some = str(some).strip()
    if some.lower() == "now": return TIME.now()
    if some.replace(".", "", 1).isdigit(): return TIME.fromtimestamp(float(some))
    if TIME.isInterval(some): return TIME.Interval(some)
    if TIME.isIntervals(some): return TIME.Intervals(some)
    some = some.replace("T", "")
    if re.search(r"^(\d{4}-\d{2}-\d{2})$", some): return TIME.strptime(some, '%Y-%m-%d')
    if re.search(r"^(\d{2}/\d{2}/\d{2}$", some): return TIME.strptime(some, '%m/%d/%y')
    if re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", some): return TIME.strptime(some, '%Y-%m-%d %H:%M:%S')
    if re.search(r"^(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})$", some): return TIME.strptime(some, '%m/%d/%y %H:%M:%S')
    if re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.(\d{3}|\d{6}))$", some): return TIME.strptime(some, '%Y-%m-%d %H:%M:%S.%f')
    if re.search(r"^(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}.(\d{3}|\d{6}))$", some): return TIME.strptime(some, '%m/%d/%y %H:%M:%S.%f')
    else: return None

  def TimezoneStr(dt:None|datetime=None, format:str="%Y-%m-%dT%H:%M:%S.%f", zone:None|str=None):
    timezone = tzlocal.get_localzone() if zone is None else pytz.timezone(zone)
    dt = datetime.now(timezone) if dt is None else dt.astimezone(timezone)
    dt_zoon_str = dt.strftime(format) + dt.strftime("%z")
    return dt_zoon_str[:-2] + ":" + dt_zoon_str[-2:]
  
  def __str__(self):
    return self.strftime("%Y-%m-%d %H:%M:%S.%f")

#------------------------------------------------------------------------------ Colors

class Color():
  RED = "\033[31m"
  GREEN = "\033[32m"
  BLUE = "\033[34m"
  YELLOW = "\033[33m"
  MAGENTA = "\033[35m"
  CYAN = "\033[36m"
  GREY = "\033[90m"
  ORANGE = "\033[38;2;206;145;120m"
  TEAL = "\033[38;2;32;178;170m"
  END = "\033[00m"

class IcoSymbols():
  INF = "💬"
  ERR = "🚨"
  WRN = "💡"
  OK  = "✅"
  DOC = "📄"
  YEA = "🚀"

class IcoText():
  INF = f"{Color.BLUE}INF{Color.END}"
  ERR = f"{Color.RED}ERR{Color.END}"
  WRN = f"{Color.YELLOW}WRN{Color.END}"
  OK  = f"{Color.GREEN}INF{Color.END}"
  DOC = f"{Color.CYAN}INF{Color.END}"
  YEA = f"{Color.CYAN}INF{Color.END}"

class Ico(IcoText):
  pass

#------------------------------------------------------------------------------
