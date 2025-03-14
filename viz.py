from owlready2 import *
import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

onto_path.append("/Users/cheongh/git/PSO-fenics/")
obo = get_namespace("http://purl.obolibrary.org/obo/")
pso = get_ontology("/Users/cheongh/git/PSO-fenics/pso.owl").load()
onto = get_ontology("/Users/cheongh/git/PSO-fenics/new.owl").load()

results = list(default_world.sparql_query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    select ?x ?y ?z where {
        ?x rdf:type owl:NamedIndividual .
        ?z rdf:type owl:NamedIndividual .
        ?x ?y ?z .
    }
"""))

G = nx.Graph()

for r in results:
    G.add_edges_from([(r[0].name, r[2].name, {"label": r[1].name})])
    print(r[0].name, r[1].name, r[2].name)

# Plot Networkx instance of RDF Graph
# pos = nx.spring_layout(G, scale=1)
# edge_labels = nx.get_edge_attributes(G, "label")
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
nx.draw(G, with_labels=True, pos=nx.spring_layout(G))

plt.show()

'''
g = default_world.as_rdflib_graph()
print(g)

G = rdflib_to_networkx_multidigraph(g)
print(G.nodes)
exit()

# Plot Networkx instance of RDF Graph
pos = nx.spring_layout(G, scale=2)
edge_labels = nx.get_edge_attributes(G, 'r')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
nx.draw(G, with_labels=True)

#if not in interactive mode for
plt.show()
'''