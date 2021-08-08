# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 23:49:53 2020

@author: chenw
"""

import argparse
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


# =============================================================================
# Parameter processing
# =============================================================================
parser = argparse.ArgumentParser()

parser.add_argument(
    '-c', '--cmd', dest='cmd_file_name', type=str, required=True,
    help='Command list file'
)

parser.add_argument(
    '-t', '--thread_num', dest='thread_num', type=int, default=2,
    help='Number of threads (default 2)'
)

args = parser.parse_args()
thread_num = args.thread_num
cmd_file_name = args.cmd_file_name


# =============================================================================
# Run in parallel
# =============================================================================
# Create a thread pool
executor = ThreadPoolExecutor(max_workers=thread_num)
task_list = list()

# Define a function to run the command
def run_cmd(cmd):
    run = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.stdout.write(str(run.stdout, encoding="utf-8"))
    sys.stderr.write(str(run.stderr, encoding="utf-8"))
    return run.returncode

# Read command list file and submit to the thread pool
with open(cmd_file_name) as cmd_file:
    for line in cmd_file:
        if line[0] == '#':
            continue
        cmd = line.strip()
        task = executor.submit(run_cmd, (cmd))
        task_list.append(task)

# Wait for all tasks to finish
for _ in as_completed(task_list):
    pass
