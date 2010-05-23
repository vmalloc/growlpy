#! /usr/bin/python
## See LICENSE for license info
import os
import sys
import subprocess

base_dir= os.path.realpath(os.path.join(os.path.dirname(__file__)))
test_dir = os.path.join(base_dir, base_dir)
sys.path.insert(0, base_dir)

if __name__ == '__main__':
    p = subprocess.Popen(["nosetests", test_dir], shell=True, env=dict(PYTHONPATH=":".join(sys.path)))
    sys.exit(p.wait())
