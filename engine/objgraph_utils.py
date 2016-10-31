#   Copyright Alexander Baranin 2016

# debugging tool to print reloadable instances

import objgraph

def print_proxies(typename_part, depth):
    labels = [x for x in objgraph.by_type('Reloadable') if typename_part in str(x)]
    if len(labels) > 0:
        objgraph.show_backrefs(labels, max_depth=depth, 
                                filename=os.path.join(os.getcwd(),'graph.png'))