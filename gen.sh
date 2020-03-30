output=data

n_agents=5
#n_dom=100
repo_size=10

p1=0.8
p2=0.6
max_arity=2
max_cost=100


for n_dom in 5; do
  for rep in $(seq 0 $repo_size); do
    name=$output/random_a${n_agents}_d${n_dom}_r$rep
    python src/dcop_gen_rand.py --agts $n_agents \
                                --doms $n_dom \
                                --p1 $p1 \
                                --p2 $p2 \
                                --max_arity $max_arity \
                                --max_cost $max_cost \
                                --name $name \
                                --ofile $name
  done
done

rm $output/*.dalo
rm $output/*.wcsp
rm $output/*.maxsum
rm $output/*.json