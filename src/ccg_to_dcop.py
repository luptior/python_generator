import numpy as np
from src import commons as cm
import sys, getopt, os

def read_ccg(fname):
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    vars = {}
    edges = {}
    read_vtype = False
    read_assignment = False

    for i, line in enumerate(content):
        L = line.split()
        if L[0] == 'v':
            vars[int(L[1])] = {'weight': float(L[2]), 'type': None, 'val': None, 'con': [],
                               'id': int(L[1])}
        elif L[0] == 'e':
            edges[i] = []
            edges[i].append(int(L[1]))
            edges[i].append(int(L[2]))
            vars[int(L[1])]['con'].append(i)
            vars[int(L[2])]['con'].append(i)

        if 'vertex types end' in line:
            read_vtype = False
        elif 'assignments end' in line:
            read_assignment = False

        if read_vtype:
            if int(L[0]) not in vars:
                vars[int(L[0])] = {'weight': 0.0, 'type': None, 'val': None, 'con': [], 'id': int(L[0])}
            vars[int(L[0])]['type'] = int(L[1])
        elif read_assignment:
            vars[int(L[0])]['val'] = int(L[1])

        if 'vertex types begin' in line:
            read_vtype = True
        elif 'assignments begin' in line:
            read_assignment = True

    return vars, edges


def is_in_kernel(var):
    return var['val'] is None


def make_wcsp(vars, edges):

    def is_decision_var(v):
        return vars[v]['type'] == 0

    def get_scope(c):
        return edges[c] if c in edges else []

    def get_constraints(v):
        return vars[v]['con'] if v in vars else []

    def get_other_var(c, v):
        return get_scope(c)[0] if get_scope(c)[1] == v else get_scope(c)[1]

    def is_connected(v, v_removed, explored_c=[]):
        if v in v_removed:
            return -1
        if is_decision_var(v):
            return v

        for c in get_constraints(v):
            if c in explored_c:
                continue
            explored_c.append(c)

            if len(get_scope(c)) == 1:
                continue
            u = get_other_var(c, v)
            con_v = is_connected(u, v_removed, explored_c)
            if con_v >= 0:
                return con_v

        return -1

    def rm_edge(e):
        if e in edges:
            del edges[e]

    def rm_var(v):
        if v in vars:
            for c in get_constraints(v):
                rm_edge(c)
            del vars[v]


    unary = {}
    edges_to_remove = []
    vars_to_remove = []

    for vi in vars:
        vi_val = vars[vi]['val']
        # add agent
        vars[vi]['agt'] = 'a' + str(vi)  if is_decision_var(vi) else None

        # If vi's value was set (NOT IN THE KERNEL)
        if not is_in_kernel(vars[vi]):
            # For each binary constraint c involving vi and some vj in the KERNEL,
            # transform c into a unary constraint.
            for cidx in vars[vi]['con']:
                
                vj = get_other_var(cidx, vi)
                vj_val = vars[vj]['val']

                if is_in_kernel(vars[vj]):
                    w0 = np.inf if (vi_val == 0) else 0.0
                    w1 = 0.0
                    if vj not in unary:
                        unary[vj] = [w0, w1]
                    else:
                        unary[vj][0] += w0
                        unary[vj][1] += w1
                elif vi_val == 0 and vj_val == 0:
                    print('Problem is UNSAT')
                    exit(-2)

                edges_to_remove.append(cidx)
            vars_to_remove.append(vi)
            # v not in kernel

    assigned_vars = {}
    for v in vars_to_remove:
        assigned_vars[v] = vars[v]['val']

    # print("variables with decisions: ", len(vars_to_remove))
    # print("vars: ", vars_to_remove)
    # print("edges: ", edges_to_remove)

    ##########################
    # Esnure can reach a decision variable
    for v in vars:
        if v not in vars_to_remove:
            explored_c = []
            u = is_connected(v, vars_to_remove, explored_c)
            if u == -1:
                vars_to_remove.append(v)
            else:
                vars[v]['agt'] = vars[u]['agt']

    # print("vars: ", vars_to_remove)
    for v in vars_to_remove:
        rm_var(v)
        if v in unary:
            del unary[v]
    for c in edges_to_remove:
        rm_edge(c)
    #########################


    for v in vars:
        if v in unary:
            unary[v][1] += vars[v]['weight']
        else:
            unary[v] = [0.0, vars[v]['weight']]

    binary = {}
    for c in edges:
        binary[c] = [np.inf, 0.0, 0.0, 0.0]

    wcsp = {'variables': {},
            'constraints': {},
            'assigned_vars': {}}

    for v in vars:
        wcsp['variables']['v' + str(v)] = {
            'id': vars[v]['id'],
            'domain': [0, 1],
            'agent' : vars[v]['agt'], #''a' + str(v) if vars[v]['type'] >= 0 else None,
            'value' : None,
            'type'  : vars[v]['type'],
            'cons'  : []
        }
    for v in assigned_vars:
        wcsp['assigned_vars']['v' +str(v)] = assigned_vars[v]

    c_id = 0
    for u in unary:
        vname = 'v'+str(u)
        cname = 'c'+str(c_id)
        wcsp['constraints'][cname] = {'scope': [vname], 'vals' : unary[u]}
        wcsp['variables'][vname]['cons'].append(cname)
        c_id += 1

    for b in binary:
        v1name, v2name = 'v'+str(edges[b][0]), 'v'+str(edges[b][1])
        cname = 'c'+str(c_id)
        wcsp['constraints'][cname] = {'scope': [v1name, v2name], 'vals': binary[b]}
        wcsp['variables'][v1name]['cons'].append(cname)
        wcsp['variables'][v2name]['cons'].append(cname)
        c_id+=1

    return wcsp


def make_dcop(wcsp):
    def is_decision_var(vname):
        return wcsp['variables'][vname]['type'] == 0

    def get_vid(vname):
        return int(wcsp['variables'][vname]['id'])

    def get_scope(cname):
        return wcsp['constraints'][cname]['scope']

    def get_constraints(vname):
        return wcsp['variables'][vname]['cons']

    def find_var(c, v, explored_c=[]):
        if len(get_scope(c)) == 1:
            return None
        other_v = get_scope(c)[0] if (get_scope(c)[1] == v) else get_scope(c)[1]
        if is_decision_var(other_v):
            return other_v
        else:
            explored_c.append(c)
            for other_c in get_constraints(other_v):
                if other_c not in explored_c:
                    a = find_var(other_c, other_v, explored_c)
                    if a is not None:
                        return a
        return None

    # Assign each aux variable u to the agent which is managing the decision variable v
    # for v in wcsp['variables']:
    #     if not is_decision_var(v):
    #         C = get_constraints(v)
    #         min_id = 999999; min_vname = None
    #
    #         for c in C:
    #             for u in get_scope(c):
    #                 if is_decision_var(u) and get_vid(u) < min_id:
    #                     min_id = get_vid(u); min_vname = u
    #
    #         if min_vname is None or wcsp['variables'][min_vname]['agent'] is None:
    #             for c in C:
    #                 min_vname = find_var(c, v)
    #                 if min_vname is not None:
    #                     wcsp['variables'][v]['agent'] = wcsp['variables'][min_vname]['agent']
    #                     break
    #         assert(min_vname is not None and wcsp['variables'][min_vname]['agent'] is not None)


    wcsp['agents'] = {}
    aid = 0
    for v in wcsp['variables']:
        agt = wcsp['variables'][v]['agent']
        if agt not in wcsp['agents']:
            wcsp['agents'][agt] = {'id': aid, 'vars': []}
            aid += 1
        wcsp['agents'][agt]['vars'].append(v)

    for c in wcsp['constraints']:
        for i, val in enumerate(wcsp['constraints'][c]['vals']):
            if np.isinf(val):
                wcsp['constraints'][c]['vals'][i] = -9999.0

    return wcsp
    # connected to u with some constraint


def main(argv):
    in_file = ''
    out_file = ''
    def rise_exception():
        print('main.py -i <input> -o <outputfile>')
        sys.exit(2)

    try:
        opts, args = getopt.getopt(argv, "i:o:h", ["ifile=", "ofile=", "help"])
    except getopt.GetoptError:
        rise_exception()
    if len(opts) != 2:
        rise_exception()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('main.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            in_file = arg
        elif opt in ("-o", "--ofile"):
            out_file = arg
    return in_file, out_file


if __name__ == '__main__':
    fname, outfile = main(sys.argv[1:])

    vars_dic, edges_dic = read_ccg(fname)
    wcsp = make_wcsp(vars_dic, edges_dic)
    # check if wcsp is solved:
    solved = True
    for v in wcsp['variables']:
        if wcsp['variables'][v]['type'] == 0 and wcsp['variables'][v]['value'] is None:
            solved = False
            break
    if solved:
        print('Problem already solved')
        exit(1)
    else:
        dcop = make_dcop(wcsp)
        print('saving dcop: agents=', len(dcop['agents']), ' variables=', len(dcop['variables']), ' constraints=', len(dcop['constraints']))
        cm.save_json_file(outfile, dcop)
