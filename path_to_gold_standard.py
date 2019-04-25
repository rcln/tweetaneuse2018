import sys, glob, re
sys.path.append("rstr_max")
import tools

print("From a directory, get a tsv like gols standard for scoring")
print("arg1 = data directory")

if len(sys.argv)<2:
  print("data directory is missing")

path_data = sys.argv[1]

path_GS = "Gold_Standards/"
tools.mkdirs(path_GS)
list_texts = glob.glob(path_data+"*/*")

list_GS = []
for path in list_texts:
  elems = re.split("/", path)
  filename = elems[-1]
  classe = elems[-2]
  list_GS.append("%s|%s"%(filename, classe))

name_GS = tools.format_name(path_data)

out_name = "%s/%s.gold"%(path_GS, name_GS)
w = open(out_name, "w")
w.write("\n".join(list_GS))
w.close()
print("Output name : %s"%out_name)
