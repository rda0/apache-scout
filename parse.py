#!/usr/bin/python3

import sys, os, glob, socket, re
import apache_conf_parser
import pprint

server_root_abs = '/etc/apache2'

indent = '    '

arg_count = 0
arg_count = len(sys.argv) - 1
#print('checking', arg_count, 'configs.')
#print('arguments', str(sys.argv))

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
    new = apache_conf_parser.SimpleDirective()
    new.arguments.append(node.arguments[0])
    path_include = strip_quotes(node.arguments[0])
    if os.path.isdir(path_include):
        path_abs = os.path.abspath(path_include)
        if path_abs.startswith(server_root_abs):
            path_include = path_abs + '/*'
        elif path_include.endswith('/'):
            path_include = path_include + '*'
        else:
            path_include = path_include + '/*'
        new.arguments.pop()
        new.arguments.append(path_include)
        new.name = node.name
        new = include_optional(new)
        return new
    if os.path.isfile(path_include) != True and os.path.islink(path_include) != True:
        path_include = server_root_abs + '/' + path_include
        if os.path.isfile(path_include) != True and os.path.islink(path_include) != True:
            new.name = 'Include(not found)'
            return new
    try:
        incl = apache_conf_parser.ApacheConfParser(path_include)
    except:
        new.name = 'Include(apache_conf_parser exception)'
        return new
    new = apache_conf_parser.ComplexDirective()
    new.header = node
    new.body.nodes = incl.nodes
    new.body.nodes = nodes_parse(new.body.nodes)
    return new

def include_optional( node ):
    new = apache_conf_parser.ComplexDirective()
    new.header = node
    for path in glob.glob(node.arguments[0]):
        incl = apache_conf_parser.SimpleDirective()
        incl.name = 'Include'
        incl.arguments.append(path)
        incl = include(incl)
        new.body.nodes.append(incl)
    return new

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

def node_print_arguments_append( node, append ):
    for arg in node.arguments:
        sys.stdout.write(arg + append)

def node_print_arguments( node ):
    node_print_arguments_append( node, ' ' )

def nodes_print_directive_append( nodes, directive, append ):
    directive = directive.lower()
    for node in nodes:
        if isinstance(node, apache_conf_parser.ComplexDirective):
            if node.name.lower() == directive:
                sys.stdout.write(node.name + ' ')
                node_print_arguments(node)
                sys.stdout.write(append)
            nodes_print_directive_append(node.body.nodes, directive, append)
        elif isinstance(node, apache_conf_parser.SimpleDirective):
            if node.name.lower() == directive:
                sys.stdout.write(node.name + ' ')
                node_print_arguments(node)
                sys.stdout.write(append)

#def nodes_print_directive_append_match( nodes, directive, append, match ):
#    directive = directive.lower()
#    for node in nodes:
#        if isinstance(node, apache_conf_parser.ComplexDirective):
#            if node.name.lower() == directive:
#                m = re.search(match, ' '.join(node.arguments))
#                if node
#                sys.stdout.write(node.name + ' ')
#                node_print_arguments(node)
#                sys.stdout.write(append)
#            nodes_print_directive_append(node.body.nodes, directive, append)
#        elif isinstance(node, apache_conf_parser.SimpleDirective):
#            if node.name.lower() == directive:
#                sys.stdout.write(node.name + ' ')
#                node_print_arguments(node)
#                sys.stdout.write(append)

def nodes_print_directive( nodes, directive ):
    nodes_print_directive_append(nodes, directive, '\n')

def nodes_print_directive_args( nodes, directive ):
    nodes_print_directive_args_append( nodes, directive, '\n')

def nodes_print_directive_args_append( nodes, directive, append ):
    directive = directive.lower()
    for node in nodes:
        if isinstance(node, apache_conf_parser.ComplexDirective):
            if node.name.lower() == directive:
                for arg in node.arguments:
                    sys.stdout.write(arg + append)
            nodes_print_directive_args_append(node.body.nodes, directive, append)
        elif isinstance(node, apache_conf_parser.SimpleDirective):
            if node.name.lower() == directive:
                for arg in node.arguments:
                    sys.stdout.write(arg + append)
 
def nodes_print_vhost_table_virtualhost( nodes, arg ):
    for node in nodes:
        if isinstance(node, apache_conf_parser.ComplexDirective):
            if node.name.lower() == 'virtualhost':
                if node.arguments[0].lower().endswith(arg):
                    sys.stdout.write(node.arguments[0].split(':')[0])
                    sys.stdout.write(' | ')
                    nodes_print_directive_args_append(node.body.nodes, 'ServerName', '')
                    sys.stdout.write(' | ')
                    nodes_print_directive_args_append(node.body.nodes, 'ServerAlias', '<br/>')
                    sys.stdout.write(' | ')
                    nodes_print_directive_args_append(node.body.nodes, 'DocumentRoot', '')
                    sys.stdout.write(' | ')
                    nodes_print_directive_append(node.body.nodes, 'RedirectMatch', '<br/>')
                    nodes_print_directive_append(node.body.nodes, 'Redirect', '<br/>')
                    sys.stdout.write('\n')
            else:
                nodes_print_vhost_table_virtualhost(node.body.nodes, arg)


def nodes_print_vhost_table( nodes, arg ):
    print('Listen | ServerName | ServerAlias | DocumentRoot | Redirect HTTPS')
    print('--- | --- | --- | --- | ---')
    nodes_print_vhost_table_virtualhost(nodes, arg)

def nodes_print_vhost_markdown( nodes ):
    print('# vhost report of', socket.gethostname())
    print('## http vhosts')
    nodes_print_vhost_table( nodes, ':80' )
    print('## https vhosts')
    nodes_print_vhost_table( nodes, ':443' )

def main( argv ):
    global server_root_abs
    usage = 'usage:', sys.argv[0], '<conf> [apache2_server_root]'
    if arg_count >= 1 and arg_count <= 4:
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
    
    if arg_count == 3:
        directive = str(sys.argv[3])
        nodes_print_directive(conf.nodes, directive)
        sys.exit(os.EX_OK)

    if arg_count == 4:
        operation = str(sys.argv[3])
        argument = str(sys.argv[4])
        if operation == 'print':
            nodes_print(conf.nodes, 0)
        elif operation == 'print_directive':
            nodes_print_directive(conf.nodes, argument)
        elif operation == 'print_directive_args':
            nodes_print_directive_args(conf.nodes, argument)
        elif operation == 'print_all':
            if argument == 'dns':
                nodes_print_directive_args(conf.nodes, 'servername')
                nodes_print_directive_args(conf.nodes, 'serveralias')
            else:
                print('operation:', operation, argument, 'not implemented')
        elif operation == 'markdown':
            if argument == 'vhost_table':
                nodes_print_vhost_markdown(conf.nodes)
            else:
                print('operation:', operation, argument, 'not implemented')
        else:
            print('operation:', operation, 'not implemented')
        sys.exit(os.EX_OK)

    nodes_print(conf.nodes, 0)

    sys.exit(os.EX_OK)

if __name__ == "__main__":
    main(sys.argv)
