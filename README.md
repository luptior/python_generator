# Exampels

## Random Generator
    dcop_gen_rand.py --agts 2 --doms 3 --p1 1.0 --p2 0.5 --max_arity 2 --max_cost 100 --name test --ofile test

    Parameters:
    agts (int) – the number of nodes
    doms (int) – the size of the domains
    p1 (float) – the constraint graph density (1 = fully connected, 0 = disconnected)
    p2 (float) – the constraint tightness (1 = full soft , 0 = full hard)
    max_arity (int) – the maximum constraint arity
    max_cost (int) - the maximum cost of a constraint value
    name (str) the name of the instance
    ofile (str) path to the output files

    Generates a Random instance according to the above parameters


## Grid Generator
    dcop_gen_grid.py --agts 2 --doms 3 --p2 0.5 --max_arity 2 --max_cost 100 --name test --ofile test

    Parameters:
    agts (int) – the number of nodes along 1 side of the grid-graph
    doms (int) – the size of the domains
    p2 (float) – the constraint tightness (1 = full soft , 0 = full hard)
    max_arity (int) – the maximum constraint arity
    max_cost (int) - the maximum cost of a constraint value
    name (str) the name of the instance
    ofile (str) path to the output files


    Generate a planar grid graph whose nodes is agts^2


## Scale-Free Generator

    dcop_gen_grid.py --agts 2 --doms 3 --m 4 --t 0.3 --p2 0.5 --max_arity 2 --max_cost 100 --name test --ofile test

    Parameters:
    agts (int) – the number of nodes
    doms (int) – the size of the domains
    m (int) – the number of random edges to add for each new node
    p (float) – Probability of adding a triangle after adding a random edge
    p2 (float) – the constraint tightness (1 = full soft , 0 = full hard)
    max_arity (int) – the maximum constraint arity
    max_cost (int) - the maximum cost of a constraint value
    name (str) the name of the instance
    ofile (str) path to the output files

    Holme and Kim algorithm for growing graphs with powerlaw degree distribution and approximate average clustering.
    The average clustering has a hard time getting above a certain cutoff that depends on m. This cutoff is often
    quite low. The transitivity (fraction of triangles to possible triangles) seems to decrease with network size.
    It is essentially the Barabási–Albert (BA) growth model with an extra step that each random edge is followed by
    a chance of making an edge to one of its neighbors too (and thus a triangle).

