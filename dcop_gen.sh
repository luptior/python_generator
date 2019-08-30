#!/bin/bash
#python dcop_gen_rand.py -a 50 -d 10 -p 0.5 -r 2 -c 100 -n random -o instances/random

for i in {0..50}
  python dcop_gen_rand_py -a $1 -d $2 -p $3 -r $4 -c $5 -n random -o instances/
