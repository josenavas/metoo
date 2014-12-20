# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The framework Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

import networkx as nx

from framework.core.base import BaseObject


class Program(BaseObject):
    """Models a program on the system

    Attributes
    ----------

    See Also
    --------
    BaseObject
    Workflow
    Method
    """

    def __init__(self, name, description, uri, input_parameters,
                 output_parameters):
        self._set_base_properties(name, description, uri)
        self._input_parameters = input_parameters
        self._output_parameters = output_parameters


class Method(Program):
    def __init__(self, function, **kwargs):
        super(Method, self).__init__(**kwargs)
        self._function = function

    def __call__(self):
        # submit the method - return TASK( ipython_UUID )
        pass


class Workflow(Program):
    """
    """
    def __init__(self, dag, **kwargs):
        super(Workflow, self).__init__(**kwargs)
        self._dag = dag

    def __call__(self, **kwargs):
        """Traverses the DAG submitting each node to compute

        Notes
        -----
        Adapted from
        http://ipython.org/ipython-doc/dev/parallel/dag_dependencies.html
        """
        # Dictionary keyed by node name and holds the Ipythhon's async
        # result object of each submission done
        async_results = {}
        # In order to define the dependencies at submission time, we need to
        # submit the nodes in topological order, so the async_result objects
        # are available to Ipython and it knows which nodes he should wait to
        # in order to start executing a node
        for node_name in nx.topological_sort(self._dag):
            # Get the current node
            node = self._dag.node[node_name]
            # Get the program object stored in the dag
            program = node['program']
            # Get the input_parameters for the program
            input_parameters = program.input_parameters

            # We now check if the current node depends on any other node
            deps = []
            input_mappings = {}
            for predecessor_name in self._dag.predecessors(node_name):
                # Add the async_results of the predecessor to the current node
                # dependency list
                deps.append(async_results[predecessor_name])
                # The edge connecting the predecessor node and the current
                # node will define how these nodes are connected
                edge = self._dag.edge[predecessor_name][node_name]
                connections = edge['connections']
                input_mappings[predecessor_name] = connections

            async_result, job_id = submit()


            job_name = node['job_name']
            kwargs = {}

            
            dep_results = {}
            kwargs['dep_results'] = dep_results
            for predecessor_name in self._dag.predecessors(node_name):
                predecessor_result = async_results[predecessor_name]
                deps.append(predecessor_result)

                if requires_deps:
                    dep_results[predecessor_name] = predecessor_result.get()

            async_results[node_name] = self._submit_with_deps(deps, job_name, func, *args, **kwargs)


    @classmethod
    def from_file(cls, fp):
        raise NotImplementedError()

    @classmethod
    def from_function(cls, func):
        return cls(func())
