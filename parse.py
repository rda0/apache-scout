#!/usr/bin/python3

import sys
import apache_conf_parser
import pprint

path_config = '/home/maedersv/tmp/vhosts.conf'

# todo: add handling for relative (to ServerRoot) vs absolute path
path_serverroot = '/etc/apache2'

indent = '    '

arguments = 0
arguments = len(sys.argv) - 1
print('checking', arguments, 'configs.')
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

def node_parse( node ):
    if isinstance(node, apache_conf_parser.ComplexDirective):
        node.body.nodes = nodes_parse(node.body.nodes)
    elif isinstance(node, apache_conf_parser.SimpleDirective):
        if node.name.lower() == 'include':
            path_include = strip_quotes(node.arguments[0])
            incl = apache_conf_parser.ApacheConfParser(path_include)
            new = apache_conf_parser.ComplexDirective()
            new.header = node
            new.body.nodes = incl.nodes
            node = new
            node.body.nodes = nodes_parse(node.body.nodes)
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
    conf = apache_conf_parser.ApacheConfParser(path_config)
    conf.nodes = nodes_parse(conf.nodes)
    nodes_print(conf.nodes, 0)

if __name__ == "__main__":
    main(sys.argv)
