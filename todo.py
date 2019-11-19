#!/bin/python3
import argparse
import time as t
import todo_pb2 as td
from pathlib import Path

class colors:
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'

day = 86400

def remove_prefix(text, prefix):
  if text.startswith(prefix):
    return text[len(prefix):]
  return text

def print_tree_dir(dir_path):
  pretty_dir_name = colors.bg.purple + dir_path.name + colors.reset
  return pretty_dir_name

def print_tree_file(file_path):
  item = td.ListItem()
  item.ParseFromString(file_path.read_bytes())
  item_age = t.time() - item.creation_time
  item_color = colors.fg.green
  if (item_age > (3 * day)):
    item_color = colors.fg.red
  elif (item_age > (2 * day)):
    item_color = colors.fg.orange
  elif (item_age > (1 * day)):
    item_color = colors.fg.yellow
  pretty_item_name = item_color + "[{:.4f} days old] ".format(item_age / day) + item.name + colors.reset
  return pretty_item_name

def add_tag(item, newtag):
  itemtag = item.tags.add()
  itemtag = newtag

def print_tree(dir):
  file_list = sorted(dir.rglob("*"))
  for path_item in file_list:
    tree_line = "  " * len(path_item.parts)
    if path_item.is_dir():
      tree_line = tree_line + print_tree_dir(path_item)
    elif path_item.is_file():
      tree_line = tree_line + print_tree_file(path_item)
    else:
      tree_line = "Unexpected item at " + tree_line
    print(tree_line)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--important", help="Specify item as important", action="store_true")
parser.add_argument("-u", "--urgent", help="Specify item as urgent", action="store_true")
parser.add_argument("-f", "--folder", help="Specify a folder to place todo item under.")
parser.add_argument("-d", "--deadline", help="Specify a deadline for the task, in YYYY-MM-DD format.")
parser.add_argument("-x", "--complete", help="Mark a task as completed.")
parser.add_argument("reminder", nargs=argparse.REMAINDER)
args = parser.parse_args()
reminder = ' '.join(args.reminder)

todo_path = Path.home() / '.todo'
folder_path = todo_path
new_folder = False

if args.folder:
  safe_path = remove_prefix(args.folder, "/")
  safe_path = remove_prefix(safe_path, "./")
  safe_path = remove_prefix(safe_path, "~/")
  folder_path = todo_path / safe_path
  if not folder_path.is_dir():
    print("Creating new todo folder \"{}\" at {}".format(safe_path, folder_path))
    folder_path.mkdir(parents=True, exist_ok=True)
    new_folder = True

if reminder:
  reminder_file = reminder + ".todo"
  reminder_path = folder_path / reminder_file

  if reminder_path.is_file():
    print("Task \"{}\" already exists!".format(reminder))
  else:
    print("Creating task \"{}\"".format(reminder))
    item = td.ListItem()
    item.name = reminder
    item.creation_time = int(t.time())
    if args.important:
      add_tag(item, "Important")
    if args.urgent:
      add_tag(item, "Urgent")
    print("Writing task to file...")
    reminder_path.write_bytes(item.SerializeToString())
elif not new_folder:
  print_tree(folder_path)
