import argparse
import os, sys
import glob
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# parameter processing
parser = argparse.ArgumentParser(description='''
This script align two genome according to http://genomewiki.ucsc.edu/index.php/Whole_genome_alignment_howto.
The whole pipeline relies on lastz and such Kent’s utilities: faSize, faToTwoBit,
faSplit, axtChain, chainMergeSort, chainPreNet, chainNet, netSyntenic, netToAxt,
axtSort, axtToMaf.
''')

parser.add_argument(
    '--target_genome', dest='target_genome', type=str, required=True,
    help='Target genome'
)

parser.add_argument(
    '--query_genome', dest='query_genome', type=str, required=True,
    help='Query genome'
)

parser.add_argument(
    '--target_prefix', dest='target_prefix', type=str, required=True,
    help='Target prefix'
)

parser.add_argument(
    '--query_prefix', dest='query_prefix', type=str, required=True,
    help='Query prefix'
)

parser.add_argument(
    '--lastz', dest='lastz_parameter', type=str, default="O=400 E=30 K=3000 L=3000 H=2200 T=1 --format=axt --ambiguous=n --ambiguous=iupac",
    help='lastz parameter (default O=400 E=30 K=3000 L=3000 H=2200 T=1 --format=axt --ambiguous=n --ambiguous=iupac)'
)

parser.add_argument(
    '--chain', dest='axtChain_parameter', type=str, default="-minScore=3000 -linearGap=medium",
    help='axtChain parameter (default -minScore=3000 -linearGap=medium)'
)

parser.add_argument(
    '--thread_num', dest='thread_num', type=int, default=8,
    help='Number of threads (default 8)'
)

args = parser.parse_args()
target_genome = args.target_genome
query_genome = args.query_genome
target_prefix = args.target_prefix
query_prefix = args.query_prefix
lastz_parameter = args.lastz_parameter
axtChain_parameter = args.axtChain_parameter
thread_num = args.thread_num

fa_path = "fa"
axt_path = "axt"
chain_path = "chain"


def run_cmd(cmd):
    run = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.stdout.write(str(run.stdout, encoding="utf-8"))
    sys.stderr.write(str(run.stderr, encoding="utf-8"))
    return run.returncode


# step 0: Preparation
cmd_file = open("prepare.sh", 'w')
cmd_file.write("#!/bin/bash\n")

executor = ThreadPoolExecutor(max_workers=thread_num)
task_list = list()

cmd = "faToTwoBit {0} {1}.2bit".format(target_genome, target_prefix)
task = executor.submit(run_cmd, (cmd))
task_list.append(task)
cmd_file.write(cmd + '\n')

cmd = "faToTwoBit {0} {1}.2bit".format(query_genome, query_prefix)
task = executor.submit(run_cmd, (cmd))
task_list.append(task)
cmd_file.write(cmd + '\n')

cmd = "faSize {0} -detailed > {1}.sizes".format(target_genome, target_prefix)
task = executor.submit(run_cmd, (cmd))
task_list.append(task)
cmd_file.write(cmd + '\n')

cmd = "faSize {0} -detailed > {1}.sizes".format(query_genome, query_prefix)
task = executor.submit(run_cmd, (cmd))
task_list.append(task)
cmd_file.write(cmd + '\n')

if not os.path.exists(fa_path):
    os.makedirs(fa_path)

cmd = "faSplit byName {0} {1}/".format(target_genome, fa_path)
task = executor.submit(run_cmd, (cmd))
task_list.append(task)
cmd_file.write(cmd + '\n')

# wait for all tasks to complete
for _ in as_completed(task_list):
    pass

executor.shutdown()

cmd_file.close()


# step 1: Alignments with lastz
cmd_file = open("lastz.sh", 'w')
cmd_file.write("#!/bin/bash\n")

executor = ThreadPoolExecutor(max_workers=thread_num)
task_list = list()

if not os.path.exists(axt_path):
    os.makedirs(axt_path)

for fa in glob.glob("{}/*.fa".format(fa_path)):
    name = fa.split('/')[-1][:-3]
    cmd = "lastz {0}[nameparse=darkspace] {1}[nameparse=darkspace] {2} ‑‑allocate:traceback=1024M > {3}/{4}.axt".format(fa, query_genome, lastz_parameter, axt_path, name)
    task = executor.submit(run_cmd, (cmd))
    task_list.append(task)
    cmd_file.write(cmd + '\n')

for _ in as_completed(task_list):
    pass
executor.shutdown()

cmd_file.close()


# step 2: Chaining
cmd_file = open("chain.sh", 'w')
cmd_file.write("#!/bin/bash\n")

executor = ThreadPoolExecutor(max_workers=thread_num)
task_list = list()

if not os.path.exists(chain_path):
    os.makedirs(chain_path)

for axt in glob.glob("{}/*.axt".format(axt_path)):
    name = axt.split('/')[-1][:-4]
    cmd = "axtChain {0} {1}.2bit {2}.2bit {3}/{4}.chain {5}".format(axt, target_prefix, query_prefix, chain_path, name, axtChain_parameter)
    task = executor.submit(run_cmd, (cmd))
    task_list.append(task)
    cmd_file.write(cmd + '\n')

for _ in as_completed(task_list):
    pass
executor.shutdown()

cmd = "chainMergeSort {}/*.chain > all.chain".format(chain_path)
run_cmd(cmd)
cmd_file.write(cmd + '\n')

cmd = "chainPreNet all.chain {0}.sizes {1}.sizes all.pre.chain".format(target_prefix, query_prefix)
run_cmd(cmd)
cmd_file.write(cmd + '\n')

cmd_file.close()


# step 3: Netting
cmd_file = open("net.sh", 'w')
cmd_file.write("#!/bin/bash\n")

cmd = "chainNet all.pre.chain -minSpace=1 {0}.sizes {1}.sizes stdout /dev/null | netSyntenic stdin noClass.net".format(target_prefix, query_prefix)
run_cmd(cmd)
cmd_file.write(cmd + '\n')

cmd_file.close()


# step 4: Maffing
cmd_file = open("maf.sh", 'w')
cmd_file.write("#!/bin/bash\n")

cmd = "netToAxt noClass.net all.pre.chain {0}.2bit {1}.2bit stdout | axtSort stdin {0}.{1}.axt".format(target_prefix, query_prefix)
run_cmd(cmd)
cmd_file.write(cmd + '\n')

cmd = "axtToMaf {0}.{1}.axt {0}.sizes {1}.sizes {0}.{1}.maf -tPrefix={0}. -qPrefix={1}.".format(target_prefix, query_prefix)
run_cmd(cmd)
cmd_file.write(cmd + '\n')

cmd_file.close()
