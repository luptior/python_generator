import random
import itertools
import json
import networkx as nx
import sys, getopt
from src import dcop_instance as dcop


def generate(G : nx.Graph, dsize = 2, p2=0.0, cost_range=(0, 10), def_cost = 0, int_cost=True, outfile=''):
    assert (0.0 <= p2 < 1.0)
    agts = {}
    vars = {}
    doms = {'0': list(range(0, dsize))}
    cons = {}
    dset = list(range(0, dsize))

    for i in range(0, len(G.nodes())):
        agts[str(i)] = None
        vars[str(i)] = {'dom': '0', 'agt': str(i)}

    cid = 0
    for e in G.edges():
        arity = len(e)
        cons[str(cid)] = {'arity': arity, 'def_cost': def_cost, 'scope': [str(x) for x in e], 'values': []}

        n_C = len(dset) ** arity
        n_forbidden_assignments = int(p2 * n_C)
        forbidden_assignments = frozenset(random.sample(range(n_C), n_forbidden_assignments))
        k = 0
        for assignments in itertools.product(*([dset, ] * arity)):
            val = {'tuple': []}
            val['tuple'] = list(assignments)
            if int_cost:
                val['cost'] = random.randint(*cost_range) if k not in forbidden_assignments else None
            else:
                val['cost'] = random.uniform(*cost_range) if k not in forbidden_assignments else None
            cons[str(cid)]['values'].append(val)
            k += 1

        cid += 1

    return agts, vars, doms, cons

def main(argv):
    agts = 10
    dsize = 2
    p2 = 0.0
    m = 5   # the number of random edges to add for each new node
    t = 0.3 # Probability of adding a triangle after adding a random edge
    max_arity = 2
    max_cost = 10
    out_file = ''
    name = ''
    def rise_exception():
        print('Input Error. Usage:\nmain.py -a -m -t -l -r -c -n -o <outputfile>')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "a:d:m:t:l:r:c:n:o:h",
                                   ["agts=","doms=", "m=", "t=", "p2=", "max_arity=", "max_cost=", "name=", "ofile=", "help"])
    except getopt.GetoptError:
        rise_exception()
    if len(opts) != 9:
        rise_exception()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('main.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-a', '--agts'):
            agts = int(arg)
        elif opt in ('-d', '--doms'):
            dsize = int(arg)
        elif opt in ('-m', '--m'):
            m = int(arg)
        elif opt in ('-t', '--t'):
            t = float(t)
        elif opt in ('-l', '--p2'):
            p2 = float(arg)
        elif opt in ('-r', '--max_arity'):
            max_arity = int(arg)
        elif opt in ('-c', '--max_cost'):
            max_cost = int(arg)
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-o", "--ofile"):
            out_file = arg

    return agts, dsize, m, t, p2, max_arity, max_cost, name, out_file


if __name__ == '__main__':
    nagts, dsize, m, t, p2, maxarity, maxcost, name, outfile = main(sys.argv[1:])

    #G = nx.scale_free_graph(nagts).to_undirected()
    G = nx.powerlaw_cluster_graph(nagts, m, t)
    while not nx.is_connected(G):
        G = nx.scale_free_graph(nagts).to_undirected()

    agts, vars, doms, cons = generate(G, dsize=dsize, p2=p2, cost_range=(0,maxcost))

    print('Creating DCOP instance ' + name, ' G nodes: ', len(G.nodes()), ' G edges:', len(G.edges()))

    dcop.create_xml_instance(name, agts, vars, doms, cons, outfile+'.xml')
    dcop.create_wcsp_instance(name, agts, vars, doms, cons, outfile+'.wcsp')
    dcop.create_json_instance(name, agts, vars, doms, cons, outfile+'.json')
    dcop.create_maxsum_instance(name, agts, vars, doms, cons, outfile+'.maxsum')
    dcop.create_dalo_instance(name, agts, vars, doms, cons, outfile+'.dalo')
