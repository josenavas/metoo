# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The framework Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------


class BaseObject(object):
    # The human readable name of the object
    name = None
    # A more detailed description of the object
    description = None
    # The uri to identify the object
    uri = None

    def _set_base_properties(self, name, description, uri):
        """Set the base properties of an object

        Parameters
        ----------
        name : str
            The human readable name of the object
        description : str
            A more detailed description of the object
        uri : str
            The uri to identify the object
        """
        self.name = name
        self.description = description
        self.uri = uri
