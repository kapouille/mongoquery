class Query(object):
    def __init__(self, definition):
        self._definition = definition

    def match(self, entry):
        return self._execute(self._definition, entry)

    def _extract(self, entry, path):
        if not path:
            return entry
        elif path[0] in entry:
            return self._extract(entry[path[0]], path[1:])
        else:
            try:
                index = int(path[0])
                return self._extract(entry[index], path[1:])
            except ValueError:
                return None

    def _execute(self, node, entry):
        for keyword, data in node.items():
            if keyword.startswith("$"):
                raise NotImplementedError()
            else:
                extracted_data = self._extract(
                    entry,
                    keyword.split(".")
                )
                return data == extracted_data
