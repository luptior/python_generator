import numpy as np
import sys, getopt, os

import commons as cm


def main(argv):
    in_file = ''
    ccg_file = ''
    out_file = ''
    s_file = ''

    def rise_exception():
        print('main.py -i <input-json> -c <input-ccg-json> -s <input_stats> -o <outputfile>')
        sys.exit(2)

    try:
        opts, args = getopt.getopt(argv, "i:c:s:o:h", ["ifile=", "ccgfile", "sfile", "ofile=", "help"])
    except getopt.GetoptError:
        rise_exception()
    if len(opts) != 4:
        rise_exception()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('main.py -i <inputfile> -c <ccgjsonfile> -s <stats-file> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            in_file = arg
        elif opt in ("-c", "--ifile"):
            in_ccg = arg
        elif opt in ("-s", "--sfile"):
            s_file = arg
        elif opt in ("-o", "--ofile"):
            out_file = arg
    return in_file, in_ccg, s_file, out_file


def get_cost(con, stats, i):
    scope = con['scope']
    values = con['vals']
    t = ''
    for vname in scope:
        t += str(stats['values'][vname][i])
    idx = int(t, 2)  # convert binary string to decimal
    return values[idx]


if __name__ == '__main__':
    fwcsp, f_ccg, fstats, outfile = main(sys.argv[1:])
    wcsp = cm.load_json_file(fwcsp)
    ccg_wcsp = cm.load_json_file(f_ccg)
    stats = cm.load_json_file(fstats)
    iters = int(stats['iterations'])
    for v in ccg_wcsp['assigned_vars']:
        stats['values'][v] = [ccg_wcsp['assigned_vars'][v]] * iters
    print('assigned vars: ', len(ccg_wcsp['assigned_vars']))

    print('iter,cost,time,load')
    best_cost = 9999999
    for i in range(int(stats['iterations'])):
        cost = 0
        for cname in wcsp['constraints']:
            cost += get_cost(wcsp['constraints'][cname], stats, i)
        if cost < best_cost:
            best_cost = cost
            print(i, best_cost, stats['simTime'][i], stats['netLoad'][i], sep=',')
