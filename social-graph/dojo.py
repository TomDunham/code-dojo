#!/usr/bin/env python
"""
An exercise in social graphing with Twitter and Graphviz

The Twitter API is documented here:

http://apiwiki.twitter.com/Twitter-API-Documentation

Use the imported Twitter class thus:

    twitter = Twitter('username', 'password')
    # notice how the method calls mirror the RESTful HTTP calls of the Twitter
    # API
    twitter.statuses.public_timeline()
    twitter.friends.ids.ntoll()
    twitter.followers.ids.ntoll()
    twitter.users.show(user_id=819606)
    # the results are returned as dictionaries mirroring the json content

Use the create_dot_file, create_styled_dot_file, and create_graph functions to 
generate a png image with Graphviz.
"""
import subprocess
from os import execvp
from string import Template
from twitter.api import Twitter

###################
# Utility Functions
###################

def create_dot_file(edge_list, root_node=None):
    """
    Generates a representation of the network in Graphviz's dot language

    edge_list: a list of the connections (edges in the directed graph) within
    the network. e.g. [[12345, 54321], [12345, 98765]] (using Twitter user ids)

    root_node: the important "user" node in the graph (optionally adds visual
    emphasis) 
    """
    # Generate the dot language input - could have used a template language like
    # Cheetah but decided this could be an exercise for the user... using
    # Python's built-in template string handling
    edges = ' '.join(['%s -> %s;' % (src, tgt) for src, tgt in edge_list])
    if root_node:
        # Visually identify the important "root" node
        node_def = 'node [shape = doublecircle]; %s; node [shape = circle];'%root_node
        graph = 'digraph G { %s %s }' % (node_def, edges)
    else:
        graph = 'digraph G { %s }'%edges
    return graph

def create_styled_dot_file(user_list, edge_list):
    """
    Generates a representation of the network in Graphviz's dot language with
    additional stylistic enhancements to make it look pretty. 

    user_list: a dictionary of dictionaries where the key is the twitter
    username and the referenced dictionary is a collection of attributes to
    display. e.g. { 'ntoll': {'id': 12345, 'fullname': 'Nicholas Tollervey'}}

    edge_list: a list of the connections (edges in the directed graph) within
    the network. e.g. [['ntoll', 'tartley'], ['ntoll', 'voidspace']] (using 
    Twitter user-names )
    """
     
    NODE = '$id [label=< <table border="0" cellborder="0" cellspacing="0"'\
            ' bgcolor="#CCCCCC"> <tr> <td colspan="2" cellpadding="2"'\
            ' align="center" bgcolor="#33CCFF"> <font face="Helvetica Bold">'\
            '$id</font> </td> </tr> $rows </table> >]'
    ATTRIBUTE = '<tr> <td align="left" cellpadding="2"><font face="Helvetica'\
            ' Bold">$key</font></td> <td align="left" cellpadding="2">$value'\
            '</td> </tr>'
    node = Template(NODE)
    attribute = Template(ATTRIBUTE)
    nodes = '\n'.join([node.substitute(id=u,
        rows='\n'.join([attribute.substitute(key=k, value=v) for k, v in
        d.iteritems()])) for u, d in user_list.iteritems()])
    edges = ' '.join(['%s -> %s;'%(src, tgt) for src, tgt in edge_list])
    graph = 'digraph G { node [ fontname = "Helvetica" fontsize = 8 shape ='\
            ' "plaintext" ] %s %s }'%(nodes, edges)
    return graph

def create_graph(dot, filename="network"):
    """
    Given a graph definition in Graphviz's dot language (and an optional
    filename) will generate an image of the graph.
    """
    proc = subprocess.Popen('dot -Tpng > %s.png' % filename,
                            shell=True,
                            stdin=subprocess.PIPE
                        )
    proc.communicate(dot.encode('utf_8'))
    execvp('open', ['open', '%s.png'%filename,])

def get_list_of_friends(twitter, twitterer):
    return twitter.friends.ids.lpdojo() 

def get_list_of_followers(twitter, twitterer):
    return twitter.followers.ids.lpdojo() 

def get_graph_for_twitterer(twitter, twitterer):
    friend_list, user_list = get_names_from_ids(twitter,
            get_list_of_followers(twitter, twitterer))
    base_person = friend_list[0]
    edge_list = [[base_person, friend] for friend in friend_list[1:]]
    
    return create_styled_dot_file(user_list, edge_list)

def get_names_from_ids(twitter, ids):
   details = {}
   names = []
   for tid in ids:
       d = twitter.users.show(id=tid)
       names.append(d['screen_name'])
       details[d['screen_name']] = {'name': d['name'] or d['screen_name'],
               'followers': d['followers_count'],
               'location': d['location'] or 'unknown'}
   return names, details

if __name__ == "__main__":
    twitter = Twitter('lpdojo', 'asdfasdf')
    twitterer = 'lpdojo'
    dot_string = get_graph_for_twitterer(twitter, twitterer)
    create_graph(dot_string)
    

