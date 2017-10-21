import xml.dom.minidom as md
import xml.etree.ElementTree as ET
import json
import commons as cm


def create_xml_instance(name, agts, vars, doms, cons, fileout=''):
    """
    Creates an XML instance
    :param name: The name of the instance
    :param agts: Dict of agents:
        key: agt_name, val = null
    :param vars: Dict of variables:
        key: var_name,
        vals: 'dom' = dom_name; 'agt' = agt_name
    :param doms: Dict of domains:
        key: dom_name,
        val: array of values (integers)
    :param cons: Dict of constraints:
        key: con_name,
        vals: 'arity' = int; 'def_cost' = int, values = list of dics {v: values, c: cost}
    """

    def prettify(elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ET.tostring(elem.getroot(), encoding='utf-8', method='xml')
        reparsed = md.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")

    def dump_rel(c_values):
        s = ''
        for i, t in enumerate(c_values):
            s += str(t['cost']) + ':'
            s += ' '.join(str(x) for x in t['tuple'])
            if i < len(c_values) -1 :
                s += ' |'
        return s

    root = ET.Element('instance')
    ET.SubElement(root, 'presentation',
                name=name,
                maxConstraintArity= str(max([cons[cid]['arity'] for cid in cons])),
                maximize="false",
                format="XCSP 2.1_FRODO")

    xml_agts = ET.SubElement(root, 'agents', nbAgents=str(len(agts)))
    for aname in agts:
        ET.SubElement(xml_agts, 'agent', name='a'+aname)

    xml_vars = ET.SubElement(root, 'variables', nbVariables=str(len(vars)))
    for vname in vars:
        ET.SubElement(xml_vars, 'variable',
                      name='v'+vname,
                      domain='d'+vars[vname]['dom'],
                      agent='a'+vars[vname]['agt'])

    xml_doms = ET.SubElement(root, 'domains', nbDomains=str(len(doms)))
    for dname in doms:
        ET.SubElement(xml_doms, 'domain', name='d'+dname, nbValues=str(len(doms[dname]))).text \
            = str(doms[dname][0]) + '..' + str(doms[dname][-1])
        # = ' '.join(str(x) for x in doms[dname])

    xml_rels = ET.SubElement(root, 'relations', nbRelations=str(len(cons)))
    xml_cons = ET.SubElement(root, 'constraints', nbConstraints=str(len(cons)))

    for cname in cons:
        ET.SubElement(xml_rels, 'relation', name='r'+cname, arity=str(cons[cname]['arity']),
                      nbTuples=str(len(cons[cname]['values'])),
                      semantics='soft',
                      defaultCost=str(cons[cname]['def_cost'])
                      ).text = dump_rel(cons[cname]['values'])

        ET.SubElement(xml_cons, 'constraint', name='c'+cname, arity=str(cons[cname]['arity']),
                      scope=' '.join('v'+str(e) for e in cons[cname]['scope']),
                      reference='r'+cname)

    tree = ET.ElementTree(root)
    if fileout:
        with open(fileout, "w") as f:
            f.write(prettify(tree))
    else:
        print(prettify(tree))


def create_wcsp_instance(name, agts, vars, doms, cons, fileout=''):
    """
     Line 1:
        <Problem name> <N> <K> <C> <UB>
     where
        <N> is the number of variables (integer)
        <K> is the maximum domain size (integer)
        <C> is the total number of constraints (integer)
        <UB> is the global upper bound of the problem (long integer)
     Variables:
        <domain size of variable with index 0> ...
        <domain size of variable with index N-1>
     Constraints:
        <Arity of the constraint>
        <Index of the first variable in the scope of the constraint>
          ...
        <Index of the last variable in the scope of the constraint>
        <Default cost value>
        <Number of tuples with a cost different than the default cost>
     and for every tuple (again in one line):

    :param name: The name of the instance
    :param agts: Dict of agents:
        key: agt_name, val = null
    :param vars: Dict of variables:
        key: var_name,
        vals: 'dom' = dom_name; 'agt' = agt_name
    :param doms: Dict of domains:
        key: dom_name,
        val: array of values (integers)
    :param cons: Dict of constraints:
        key: con_name,
        vals: 'arity' = int; 'def_cost' = int, values = list of dics {v: values, c: cost}
    """
    max_d = max( [len(doms[d]) for d in doms])
    s = name + ' ' + str(len(vars)) + ' ' + str(max_d) + ' ' + str(len(cons)) + ' 99999' + '\n'
    s += ' '.join( str(len(doms[vars[vname]['dom']])) for vname in vars) + '\n'
    for cname in cons:
        c = cons[cname]
        s += str(c['arity']) + ' ' + \
             ' '.join(x for x in c['scope']) + ' ' + \
             str(c['def_cost']) + ' ' + \
             str(len(c['values'])) + '\n'
        for v in c['values']:
            for vid in [x for x in v['tuple']]:
                s+= str(vid) + ' '
            s += str(v['cost']) + '\n'
            #s += ' '.join(str(vid) for vid in v['tuple']) + ' ' + str(v['cost']) + '\n'

    if fileout:
        with open(fileout, "w") as f:
            f.write(s)
    else:
        print(s)


def create_json_instance(name, agts, vars, doms, cons, fileout=''):
    """"
    It assumes constraint tables are complete
    """
    jagts = {}
    jvars = {}
    jcons = {}

    for vid in vars:
        v = vars[vid]
        d = doms[v['dom']]
        aid = v['agt']
        jvars['v'+vid] = {
            'value': None,
            'domain': d,
            'agent': 'a'+str(aid),
            'type': 1,
            'id': int(vid),
            'cons': []
        }

    for aid in agts:
        jagts['a'+aid] = {'vars': ['v'+vid for vid in vars if vars[vid]['agt'] == aid]}
        jagts['id'] = int(aid)

    for cid in cons:
        c = cons[cid]
        jcons['c'+cid] = {
            'scope': ['v'+vid for vid in c['scope']],
            'vals': [x['cost'] for x in c['values']]
        }
        for vid in c['scope']:
            jvars['v'+str(vid)]['cons'].append('c'+cid)

    instance = {'variables': jvars, 'agents': jagts, 'constraints': jcons}

    if fileout:
        #cm.save_json_file(fileout, instance)
        with open(fileout, 'w') as outfile:
            json.dump(instance, outfile, indent=2)
    else:
        print(json.dumps(instance, indent=2))


def create_maxsum_instance(name, agts, vars, doms, cons, fileout=''):
    """
    :param name: The name of the instance
    :param agts: Dict of agents:
        key: agt_name, val = null
    :param vars: Dict of variables:
        key: var_name,
        vals: 'dom' = dom_name; 'agt' = agt_name
    :param doms: Dict of domains:
        key: dom_name,
        val: array of values (integers)
    :param cons: Dict of constraints:
        key: con_name,
        vals: 'arity' = int; 'def_cost' = int, values = list of dics {v: tuples, c: cost}
    """
    s = 'AGENT 1\n'
    map_vidx = {}
    for i, vname in enumerate(vars):
        d = doms[vars[vname]['dom']]
        map_vidx[vname] = i
        
        s += 'VARIABLE ' + str(i) + ' ' + str(d[0]) + ' ' + str(d[-1]) + '\n'

    for i, cname in enumerate(cons):
        c = cons[cname]
        s += 'CONSTRAINT ' + str(i) + ' 1 '
        for x in c['scope']:
            s += str(map_vidx[x]) + ' '
          #' '.join(str(map_vidx[x]) for x in c['scope']) + '\n'
        s += '\n'

        for v in c['values']:
            s += 'F ' + ' '.join(str(t) for t in v['tuple']) + ' ' + str(v['cost']) + '\n'

    if fileout:
        with open(fileout, "w") as f:
            f.write(s)
    else:
        print(s)


def sanity_check(vars, cons):
    """ Check all variables participate in some constraint """
    v_con = []
    for c in cons:
        for x in cons[c]['scope']:
            if x not in v_con:
               v_con.append(x)
    for v in vars:
        if v not in v_con:
            return False
    return True


if __name__ == '__main__':
    agts = {'1': None}
    vars = {'1': {'dom': '1', 'agt': '1'},
            '2': {'dom': '1', 'agt': '1'}}
    doms = {'1': [0, 1]}
    cons = {'1': {'arity': 2, 'def_cost': 0, 'scope': ['1', '2'],
                   'values': [{'tuple': [0, 0], 'cost': 1}, {'tuple': [0, 1], 'cost': 2},
                              {'tuple': [1, 0], 'cost': 5}, {'tuple': [1, 1], 'cost': 3}]}}


    # create_xml_instance("test", agts, vars, doms, cons)
    # create_wcsp_instance("test", agts, vars, doms, cons)
    # create_json_instance("test", agts, vars, doms, cons)
    create_maxsum_instance("test", agts, vars, doms, cons)