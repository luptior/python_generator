"""
A parser written in python for reading the output .xml file

"""

import xml.etree.ElementTree as ET


def xml_parse(f="/Users/luptior/Desktop/Research_3/python_generator/data/a5_d100_r4.xml"):
    tree = ET.parse(f)
    root = tree.getroot()

    agents = []
    variables = {}
    domains = {}
    relations = {}
    constraints = {}

    data = {x.tag: x for x in root}

    # processing agents
    for agent in data['agents']:
        agents.append(agent.attrib['name'])

    # processing variables
    for v in data['variables']:
        variables[v.attrib["name"]] = {"agent": v.attrib["agent"]}
        variables[v.attrib["name"]]["domain"] = v.attrib["domain"]

    # processing domain
    for d in data['domains']:
        domains[d.attrib["name"]] = {'nbValues': d.attrib['nbValues']}
        domains[d.attrib["name"]]['domain_range'] = [int(x) for x in d.text.split("..")]

    # processing relations
    for r in data['relations']:
        relations[r.attrib['name']] = r.attrib
        relations[r.attrib['name']]['relations'] = \
            {tuple([int(x) for x in x.strip().split(":")[-1].split()]): int(x.strip().split(":")[0]) \
             for x in r.text.strip("|").split("|")}

    # processing constrains
    for c in data['constraints']:
        constraints[c.attrib['name']] = c.attrib
        constraints[c.attrib['name']]['scope'] = constraints[c.attrib['name']]['scope'].split()

    return agents, domains, variables, relations, constraints


if __name__ == '__main__':
    f = "/Users/luptior/Desktop/Research_3/simulation_data/random_5_d3/rep_0_random_5_d3.xml"
    print(xml_parse(f))