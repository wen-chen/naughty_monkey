## pairwise_genome_alignment
```
python3 pairwise_genome_alignment.py -h
usage: pairwise_genome_alignment.py [-h] --target_genome TARGET_GENOME
                                    --query_genome QUERY_GENOME
                                    --target_prefix TARGET_PREFIX
                                    --query_prefix QUERY_PREFIX
                                    [--lastz LASTZ_PARAMETER]
                                    [--chain AXTCHAIN_PARAMETER]
                                    [--thread_num THREAD_NUM]

This script align two genome according to
http://genomewiki.ucsc.edu/index.php/Whole_genome_alignment_howto. The whole
pipeline relies on lastz and such Kent’s utilities: faSize, faToTwoBit,
faSplit, axtChain, chainMergeSort, chainPreNet, chainNet, netSyntenic,
netToAxt, axtSort, axtToMaf.

optional arguments:
  -h, --help            show this help message and exit
  --target_genome TARGET_GENOME
                        Target genome
  --query_genome QUERY_GENOME
                        Query genome
  --target_prefix TARGET_PREFIX
                        Target prefix
  --query_prefix QUERY_PREFIX
                        Query prefix
  --lastz LASTZ_PARAMETER
                        lastz parameter (default O=400 E=30 K=3000 L=3000
                        H=2200 T=1 --format=axt --ambiguous=n
                        --ambiguous=iupac)
  --chain AXTCHAIN_PARAMETER
                        axtChain parameter (default -minScore=3000
                        -linearGap=medium)
  --thread_num THREAD_NUM
                        Number of threads (default 8)
```