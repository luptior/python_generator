#!/bin/bash
# python dcop_gen_rand.py --agts 50 --doms 3 --p1 1.0 --p2 0.5 --max_arity 2 --max_cost 100 --name test --ofile test
mkdir random
for i in {0..50}
do
  file_name="random/rep_"$i"_random"
  python dcop_gen_rand.py --agts $1 --doms 10 --p1 $2 --p2 $3 --max_arity 2 --max_cost 100 --name "test" --ofile $file_name
  echo "Generate "$file_name
done
rm random/*wcsp
rm random/*json
