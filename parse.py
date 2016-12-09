#!/usr/bin/python3

import sys, os, glob
import apache_conf_parser
import pprint

server_root_abs = '/etc/apache2'

indent = '    '

arg_count = 0
arg_count = len(sys.argv) - 1
print('checking', arg_count, 'configs.')
print('arguments', str(sys.argv))

def strip_quotes( s ):
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s

def print_indent( level ):
    "print(indent function"
    l = level - 1
    if l > 0:
        indent_multi = indent * l
        sys.stdout.write(indent_multi)

def include( node ):
    path_include = strip_quotes(node.arguments[0])
    print(path_include)
    if os.path.isfile(path_include) != True:
        path_include = server_root_abs + '/' + path_include
        print(path_include)
        if os.path.isfile(path_include) != True:
            node.name = 'Include(not found)'
            return node
    try:
        incl = apache_conf_parser.ApacheConfParser(path_include)
    except:
        node.name = 'Include(apache_conf_parser exception)'
        return node
    new = apache_conf_parser.ComplexDirective()
    new.header = node
    new.body.nodes = incl.nodes
    node = new
    node.body.nodes = nodes_parse(node.body.nodes)

def include_optional( node ):
    return node

def node_parse( node ):
    if isinstance(node, apache_conf_parser.ComplexDirective):
        node.body.nodes = nodes_parse(node.body.nodes)
    elif isinstance(node, apache_conf_parser.SimpleDirective):
        if node.name.lower() == 'include':
            node = include(node)
        elif node.name.lower() == 'includeoptional':
            node = include_optional(node)
    return node

def nodes_parse( nodes ):
    for i, node in enumerate(nodes):
        nodes[i] = node_parse(node)
    return nodes

def nodes_print( nodes, level ):
    level += 1
    for node in nodes:
        if isinstance(node, apache_conf_parser.ComplexDirective):
            print_indent(level)
            print(node.name, node.arguments)
            level = nodes_print(node.body.nodes, level)
        elif isinstance(node, apache_conf_parser.SimpleDirective):
            print_indent(level)
            print(node.name, node.arguments)
        elif isinstance(node, apache_conf_parser.Directive):
            print_indent(level)
            print('# Directive')
        elif isinstance(node, apache_conf_parser.CommentNode):
            print_indent(level)
            print('# CommentNode')
        elif isinstance(node, apache_conf_parser.BlankNode):
            print_indent(level)
            print('')
        else:
            print_indent(level)
            print('# else')
    level -= 1
    return level

def main( argv ):
    global server_root_abs
    usage = 'usage:', sys.argv[0], '<conf> [apache2_server_root]'
    if arg_count == 1 or arg_count == 2:
        conf_file = str(sys.argv[1])
        if os.path.isfile(conf_file) != True:
            print(usage)
            print('       <conf> must be a file')
            sys.exit(os.EX_USAGE)
        conf_file_abs = os.path.abspath(conf_file)
        if arg_count == 2:
            server_root = str(sys.argv[2])
            if os.path.isdir(server_root) != True:
                print(usage)
                print('       [apache2_server_root] must be a directory')
                sys.exit(os.EX_USAGE)
            server_root_abs = os.path.abspath(server_root)
    else:
        print(usage)
        sys.exit(os.EX_USAGE)
    os.chdir(server_root_abs)
    conf = apache_conf_parser.ApacheConfParser(conf_file_abs)
    conf.nodes = nodes_parse(conf.nodes)
    nodes_print(conf.nodes, 0)
    sys.exit(os.EX_OK)

if __name__ == "__main__":
    main(sys.argv)
