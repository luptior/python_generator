import random
import itertools
import json
import networkx as nx
import sys, getopt

import dcop_instance as dcop


def generate(G : nx.Graph, dsize = 2, p2=0.0, cost_range=(0, 10), def_cost = 0, int_cost=True, outfile='') :
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
    p2 = 0.0
    dsize = 2
    max_arity = 2
    max_cost = 10
    out_file = ''
    name = ''
    def rise_exception():
        print('Input Error. Usage:\nmain.py -a -d -l -r -c -n -o <outputfile>')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "a:d:l:r:c:n:o:h",
                                   ["agts=", "doms=", "p2=", "max_arity=", "max_cost=", "name=", "ofile=", "help"])
    except getopt.GetoptError:
        rise_exception()
    if len(opts) != 7:
        rise_exception()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('main.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-a', '--agts'):
            agts = int(arg)
        elif opt in ('-d', '--doms'):
            dsize = int(arg)
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
    return agts, dsize, p2, max_arity, max_cost, name, out_file

if __name__ == '__main__':
    nagts, dsize, p2, maxarity, maxcost, name, outfile = main(sys.argv[1:])

    G = nx.grid_graph([nagts, nagts]).to_undirected()
    while not nx.is_connected(G):
        G = nx.grid_graph(nagts).to_undirected()

    # Normalize Graph
    Gn = nx.empty_graph(nagts)
    map_nodes = {}
    nid = 0
    for n in G.nodes():
        map_nodes[n] = nid
        nid += 1
    for e in G.edges():
        Gn.add_edge(map_nodes[e[0]], map_nodes[e[1]])

    agts, vars, doms, cons = generate(Gn, dsize=dsize, p2=p2, cost_range=(0,maxcost))

    print('Creating DCOP instance ' + name, ' G nodes: ', len(Gn.nodes()), ' G edges:', len(Gn.edges()))

    dcop.create_xml_instance(name, agts, vars, doms, cons, outfile+'.xml')
    dcop.create_wcsp_instance(name, agts, vars, doms, cons, outfile+'.wcsp')
    dcop.create_json_instance(name, agts, vars, doms, cons, outfile+'.json')
    dcop.create_maxsum_instance(name, agts, vars, doms, cons, outfile+'.maxsum')
    dcop.create_dalo_instance(name, agts, vars, doms, cons, outfile+'.dalo')