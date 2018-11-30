import subprocess
import os
import re
import time
import sys, getopt
import shutil


def justname(source_dir:str):
    list = os.listdir(source_dir)
    for i in range(0, len(list)):
        path = os.path.join(source_dir, list[i])
        if os.path.isfile(path):
            if list[i].endswith('.mp4'):
                text_path = re.sub('.mp4','.text', path)
                with open(text_path) as f:
                    title = f.readline()
                    title = re.sub('\n', '', title)
                    d_path = os.path.join(source_dir, os.path.join(source_dir, title) + '.mp4')
                    shutil.move(path, d_path)

def apath(path:str):
    if path.startswith('.'):
        return os.path.abspath(path)
    elif path.startswith('~'):
        home = os.path.expanduser('~')
        return re.sub('~', home, path)
    else:
        return path

def main(argv):
    sdir = ""

    try:
        # 这里的 h 就表示该选项无参数，i:表示 i 选项后需要有参数
        opts, args = getopt.getopt(argv, "hd:",["dir="])
    except getopt.GetoptError:
        print('Error: param')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-d":
            print('Error: param')
            sys.exit()
        elif opt in ("-d", "--dir"):
            sdir = apath(arg)

    print('indir: ', sdir)
    justname(sdir)


if __name__ == '__main__':
     main(sys.argv[1:])
