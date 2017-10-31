#!/bin/bash
# python dcop_gen_grid.py --agts 50 --doms 10 --p2 0.5 --max_arity 2 --max_cost 100 --name test --ofile test
mkdir grid
for i in {0..50}
do
  file_name="grid/rep_"$i"_grid"
  python dcop_gen_grid.py --agts $1 --doms 10 --p2 $2 --max_arity 2 --max_cost 100 --name "test" --ofile $file_name
  echo "Generate "$file_name
done
rm grid/*wcsp
rm grid/*json
