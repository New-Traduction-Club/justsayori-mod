
init -991 python in fae_extras:

    import store

    persistent = store.persistent

    dictionary_submods = dict()

    class Extras(object):
        """
        Represents submod module registry entry.
        """

        def __init__(
            self,
            name,
            creator,
            description
        ):
            """
            Initializes a new submod entry and registers it.

            IN:
                name - str: The name of the submod.
                creator - str: The creator of the submod.
                description - str: The description of the submod.
            """

            self.name = name
            self.creator = creator
            self.description = description

            dictionary_submods[name] = self

    
        def __repr__(self):
            """
            Returns a string representation of the submod entry.

            OUT:
                str: String representation of the entry.
            """

            return str(self.name, self.creator)

        @staticmethod
        def _findSubmod(name):
            """
            Searches for a registered submod by its name.

            IN:
                name - str: The name of the submod to look up.

            OUT:
                Extras/None: The submod object if found, otherwise None.
            """

            return dictionary_submods.get(name)

    def isInstalled(name):
        """
        Checks whether a submod with the given name is installed.

        IN:
            name - str: The name of the submod to check.

        OUT:
            bool: True if the submod is registered, False otherwise.
        """

        extramod = Extras._findSubmod(name)

        return bool(extramod)
