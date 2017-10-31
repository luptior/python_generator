#!/bin/bash
#python dcop_gen_scalefree.py --agts 50 --doms 3 --m 4 --t 0.3 --p2 0.5 --max_arity 2 --max_cost 100 --name test -ofile test
mkdir scale-free
for i in {0..50}
do
  file_name="scale-free/rep_"$i"_scale-free"
  python dcop_gen_scalefree.py --agts $1 --doms 10 --m 4 --t 0.3 --p2 $2 --max_arity 2 --max_cost 100 --name "test" --ofile $file_name
  echo "Generate "$file_name
done
rm scale-free/*wcsp
rm scale-free/*json
