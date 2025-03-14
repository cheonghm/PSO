from owlready2 import *
from matplotlib import pyplot as plt
import networkx as nx
import sys, os, io
import contextlib


class Dialogue:

    def __init__(self):

        onto_path.append("/Users/cheongh/git/PSO-fenics/")
        self.obo = get_namespace("http://purl.obolibrary.org/obo/")
        self.pso = get_ontology("/Users/cheongh/git/PSO-fenics/pso.owl").load()
        self.pso_f = get_ontology("/Users/cheongh/git/PSO-fenics/pso-fenics.owl").load()

        self.bfo_object = self.obo.BFO_0000030
        self.has_participant = self.obo.RO_0000057
        self.cardinality_types = class_construct._restriction_type_2_label
        self.is_non_trivial_subclass_axiom = class_construct.Restriction
        self.existing_entities = [self.bfo_object, self.pso.fiat_object_surface]

        self.plt = plt
        self.plt.ion()

        self.text_dict = {}
        self.boundary_condition_visualized = []
        self.body_property_visualized = []

    def start(self):

        print()
        print("Start of a dialogue manager for setting up simulation for FEniCS")
        print("===============================================")
        input()

        print("- Current object to be simulated:")
        object_instances = self.bfo_object.instances()
        for i in object_instances:
            print("\t", i.name)
        print()

        print("- Surface parts of the object:")
        fos_instances = self.pso.fiat_object_surface.instances()
        for i in fos_instances:
            print("\t", i.name)
        print("===============================================")

        self.draw_model()
        self.draw_graph()
        self.plt.show()
        input()

        for i in object_instances:
            self.create_next_instance(i, self.bfo_object)

    def run_reasoner(self):

        print("Running the reasoner to check consistency...")
        with self.pso_f:
            try:
                sync_reasoner(infer_property_values=True)
                print("The ontology is consistent!")
            except owlready2.base.OwlReadyInconsistentOntologyError as e:
                print("The ontology is inconsistent! Running the Pellet reasoner to obtain explanation...")
                input()
                sync_reasoner_pellet(infer_property_values=True, debug=2)

        print("===============================================")
        print()
        input("")

    def run_reasoner_quiet(self):

        with self.pso_f:
            try:
                sys.stdout = open(os.devnull, "w")
                sys.stderr = open(os.devnull, "w")
                sync_reasoner(infer_property_values=True)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            except owlready2.base.OwlReadyInconsistentOntologyError as e:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                print("The ontology is inconsistent! Running the Pellet reasoner to obtain explanation...")
                input()
                sync_reasoner_pellet(infer_property_values=True, debug=2)

    def save_ontology(self):

        print("Saving the ontology...")
        self.pso_f.save(file="new.owl", format="rdfxml")
        print("===============================================")
        print()

    def create_next_instance(self, current_instance, current_class):

        subclass_axioms = self.obtain_subclass_axioms(current_class)

        if subclass_axioms:

            print("Let's define data related to '" + str(current_instance.name) + "'")
            print("-----------------------------------------------")
            input()

            for axiom in subclass_axioms:

                print("The following axiom should be satisfied:")

                if axiom.cardinality:
                    cardinality_string = str(self.cardinality_types[axiom.type]) + " " + str(axiom.cardinality)
                else:
                    cardinality_string = str(self.cardinality_types[axiom.type])

                print("- '" + str(current_instance.name) + "' " + str(axiom.property.label[0]) + " " +
                      cardinality_string + " " + str(axiom.value) + ".")
                input()

                if self.cardinality_types[axiom.type] == "exactly":

                    number_of_entities = int(axiom.cardinality)

                elif self.cardinality_types[axiom.type] == "min":

                    cardinality_number = int(axiom.cardinality)

                    while True:
                        try:
                            number_of_entities = int(input("How many " + str(axiom.value) + " do you want to define ["
                                                           + str(cardinality_number) + "-]? "))
                            if number_of_entities < cardinality_number:
                                print("Enter the value greater than or equal to " + str(cardinality_number) + ".")
                            else:
                                break
                        except:
                            print("Enter the value in int type")
                    print()

                elif self.cardinality_types[axiom.type] == "max":

                    while True:
                        try:
                            number_of_entities = int(input("How many " + str(axiom.value) + " do you want to define [0-"
                                                           + str(cardinality_number) + "]? "))
                            if number_of_entities > cardinality_number:
                                print("Enter the value between 0 and " + str(cardinality_number) + ".")
                            else:
                                break
                        except:
                            print("Enter the value in int type")
                    print()

                elif self.cardinality_types[axiom.type] == "some":

                    while True:
                        try:
                            number_of_entities = int(input("How many " + str(axiom.value) + " do you want to define [0-"
                                                           + "]? "))
                            if number_of_entities < 0:
                                print("Enter a non-negative int value.")
                            else:
                                break
                        except:
                            print("Enter the value in int type")
                    print()

                if number_of_entities == 0:
                    print("You have decided to not define any " + str(axiom.value) + ".")
                    input()
                else:
                    # print()
                    for i in range(0, number_of_entities):
                        if type(axiom.value) == type:
                            self.create_data_fact(current_instance, axiom)
                        else:
                            self.create_instance_fact(current_instance, axiom)
        else:
            pass

    def create_data_fact(self, current_instance, axiom):

        data_property = axiom.property.label[0]
        value_type = str(axiom.value).split('\'')[1].strip()

        if data_property == "has vector values":
            while True:
                try:
                    value = str(input("Enter the vector values of '" + str(current_instance.name) + "' separated by commas: "))
                    if "," in value:
                        break
                    else:
                        print("Enter the vector values separated by commas")
                except:
                    print("Enter the vector values separated by commas")

            self.pso_f.has_vector_values[current_instance] = [value]
            self.run_reasoner_quiet()

        else:
            if value_type == "float":
                while True:
                    try:
                        value = float(input("Enter the value of '" + str(current_instance.name) + "': "))
                        break
                    except:
                        print("Enter the value in float type")

            elif value_type == "int":
                while True:
                    try:
                        value = int(input("Enter the value of '" + str(current_instance.name) + "': "))
                        break
                    except:
                        print("Enter the value in int type")

            self.pso_f.has_value[current_instance] = [value]
            self.run_reasoner_quiet()

        print()
        print("The following fact is created:")
        print("- " + str(current_instance.name) + " " + str(axiom.property.label[0]) + " " +
              str(value) + ".")
        print("-----------------------------------------------")
        input()
        print("Moving back up... ")
        print()

    def create_instance_fact(self, current_instance, axiom):

        subclasses = list(axiom.value.subclasses())

        if subclasses:
            new_instance, subclass_associated = \
                self.create_instance_fact_with_options(subclasses, current_instance, axiom)
            self.create_next_instance(new_instance, subclass_associated)

        else:
            subclass_associated = axiom.value

            if subclass_associated in self.existing_entities:
                self.create_instance_fact_with_existing_entities(subclass_associated, current_instance, axiom)

            else:
                new_instance = self.create_instance_fact_rest(subclass_associated, current_instance, axiom)
                self.create_next_instance(new_instance, subclass_associated)

    def create_instance_fact_with_options(self, subclasses, current_instance, axiom):

        print("Which type is the " + str(axiom.value.label[0]) + "? [1-" + str(len(subclasses)) + "]")
        for i in range(0, len(subclasses)):
            print("\t" + str(i + 1) + ". " + str(subclasses[i].label[0]))

        while True:
            try:
                user_input = int(input("Enter your choice: "))
                if user_input in list(range(1, len(subclasses) + 1)):
                    print()
                    break
                else:
                    print("Invalid choice")
                    print()
            except:
                print("Enter the value in int type")

        subclass_associated = subclasses[user_input - 1]

        new_instance = subclass_associated(namespace=self.pso_f)
        axiom.property[current_instance].append(new_instance)
        self.run_reasoner_quiet()

        print("New instance named '" + str(new_instance.name) +
              "' has been created with the following fact.")
        print("- " + str(current_instance.name) + " " + str(axiom.property.label[0]) + " " +
              str(new_instance.name) + ".")
        print("-----------------------------------------------")

        self.update_model()
        self.draw_graph()
        self.plt.show()
        input()

        return new_instance, subclass_associated

    def create_instance_fact_with_existing_entities(self, subclass_associated, current_instance, axiom):

        if subclass_associated == self.existing_entities[0]:  # BFO object
            existing_instances = self.existing_entities[0].instances()
        elif subclass_associated == self.existing_entities[1]:  # PSO fiat object surface
            existing_instances = self.existing_entities[1].instances()

        print("Which of the following entities should be associated? [1-" +
              str(len(existing_instances)) + "]:")
        for i in range(0, len(existing_instances)):
            print("\t" + str(i + 1) + ". " + str(existing_instances[i].name))

        while True:
            user_input = int(input("Enter your choice: "))
            if user_input in list(range(1, len(existing_instances) + 1)):
                print()
                break
            else:
                print("Invalid choice")
                print()

        existing_instance = existing_instances[user_input - 1]
        axiom.property[current_instance].append(existing_instance)
        self.run_reasoner_quiet()

        print("The following fact is created:")
        print("- " + str(current_instance.name) + " " + str(axiom.property.label[0]) + " " +
              str(existing_instance.name) + ".")
        print("-----------------------------------------------")

        self.update_model()
        self.draw_graph()
        self.plt.show()
        input()

        print("Moving back up... ")
        print()

    def create_instance_fact_rest(self, subclass_associated, current_instance, axiom):

        new_instance = subclass_associated(namespace=self.pso_f)
        axiom.property[current_instance].append(new_instance)
        self.run_reasoner_quiet()

        print("New instance named '" + str(new_instance.name) +
              "' has been created with the following fact.")
        print("- " + str(current_instance.name) + " " + str(axiom.property.label[0]) + " " +
              str(new_instance.name) + ".")
        print("-----------------------------------------------")

        self.update_model()
        self.draw_graph()
        self.plt.show()
        input()

        return new_instance

    def obtain_subclass_axioms(self, current_class):

        all_subclass_axioms = current_class.is_a
        subclass_axioms = []

        for a in all_subclass_axioms:
            if type(a) == self.is_non_trivial_subclass_axiom:
                if self.pso_f.pso_dialogue_trigger[current_class, rdfs_subclassof, a]:
                    subclass_axioms.append(a)

        return subclass_axioms

    def draw_model(self):

        self.plt.figure(1)
        self.plt.axis('off')

        axes = self.plt.gca()
        axes.set_xlim([0, 10])
        axes.set_ylim([0, 10])

        self.plt.hlines(2.5, 2.5, 7.5)
        self.plt.hlines(7.5, 2.5, 7.5)
        self.plt.vlines(2.5, 2.5, 7.5)
        self.plt.vlines(7.5, 2.5, 7.5)

        text0 = self.plt.text(4.7, 5, 'pipe')
        text1 = self.plt.text(0.4, 5, 'pipe_surface1')
        text2 = self.plt.text(7.6, 5, 'pipe_surfece2')
        text3 = self.plt.text(4, 7.7, 'pipe_surface3')
        text4 = self.plt.text(4, 2, 'pipe_surface4')

        self.text_dict = {
            "pipe": text0,
            "pipe_surface1": text1,
            "pipe_surface2": text2,
            "pipe_surface3": text3,
            "pipe_surface4": text4
        }

    def draw_graph(self):

        self.plt.figure(2)

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

        # Plot Networkx instance of RDF Graph
        # pos = nx.spring_layout(G, scale=1)
        # edge_labels = nx.get_edge_attributes(G, "label")
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        self.plt.clf()
        nx.draw(G, with_labels=True, pos=nx.spring_layout(G))

    def update_model(self):

        self.plt.figure(1)

        blue_boundary_conditions = [
            self.pso_f.displacement_boundary_condition, self.pso_f.velocity_boundary_condition,
            self.pso_f.temperature_boundary_condition
        ]
        red_boundary_conditions = [
            self.pso_f.surface_force_boundary_condition, self.pso_f.pressure_boundary_condition,
            self.pso_f.heat_flux_boundary_condition
        ]

        for bc in self.pso.boundary_condition_situation.instances():
            for p in self.has_participant[bc]:
                if p.is_instance_of[0] == self.pso.fiat_object_surface and bc.name not in self.boundary_condition_visualized:

                    current_text_position = self.text_dict[p.name].get_position()
                    self.text_dict[p.name].set_position((current_text_position[0], current_text_position[1]+0.5))

                    if bc.is_instance_of[0] in blue_boundary_conditions:
                        text_color = "blue"
                    elif bc.is_instance_of[0] in red_boundary_conditions:
                        text_color = "red"
                    else:
                        text_color = "black"
                    self.plt.text(current_text_position[0], current_text_position[1], bc.name, color=text_color)

                    self.boundary_condition_visualized.append(bc.name)

    def test(self):

        current_class = self.bfo_object
        all_subclass_axioms = current_class.is_a


d = Dialogue()
# d.test(); exit()
d.start()
d.run_reasoner()
d.save_ontology()
print("Problem definition is complete!")
