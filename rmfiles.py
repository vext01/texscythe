import sys

if len(sys.argv) != 4:
    print("usage: rmfiles rmfile fromfile remainfile")
    sys.exit(1)

with open(sys.argv[1], "r") as fh:
    rmfiles = fh.readlines()

rmfiles = [ x.strip() for x in rmfiles ]

ih = open(sys.argv[2], "r")
oh = open(sys.argv[3], "w")
for line in ih:
    line = line.strip()
    if line not in rmfiles:
        oh.write(line + "\n")

ih.close()
oh.close()



