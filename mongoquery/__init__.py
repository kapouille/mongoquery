import re
from collections import Sequence, Mapping

try:
    string_type = basestring
except NameError:
    string_type = str


class QueryError(Exception):
    pass


class _Undefined(object):
    pass


def is_non_string_sequence(entry):
    return isinstance(entry, Sequence) and not isinstance(entry, string_type)


class Query(object):
    def __init__(self, definition):
        self._definition = definition

    def match(self, entry):
        return self._match(self._definition, entry)

    def _match(self, condition, entry):
        if isinstance(condition, Mapping):
            return all(
                self._process_condition(sub_operator, sub_condition, entry)
                for sub_operator, sub_condition in condition.items()
            )
        else:
            if is_non_string_sequence(entry):
                return condition in entry
            else:
                return condition == entry

    def _extract(self, entry, path):
        if not path:
            return entry
        if entry is None:
            return entry
        if is_non_string_sequence(entry):
            try:
                index = int(path[0])
                return self._extract(entry[index], path[1:])
            except ValueError:
                return [self._extract(item, path) for item in entry]
        elif isinstance(entry, Mapping) and path[0] in entry:
            return self._extract(entry[path[0]], path[1:])
        else:
            return _Undefined()

    def _path_exists(self, operator, condition, entry):
        if type(operator) is str:
            keys_lists = list(operator.split('.'))
        else:
            keys_lists = [ path ]
        for i, k in enumerate(keys_lists):
            if isinstance(entry, Sequence) and not k.isdigit():
              for e in entry:
                  operator = '.'.join(keys_lists[i:])
                  if self._path_exists(operator, condition, e) == condition:
                      return condition
            elif isinstance(entry, Sequence):
                k = int(k)
            try:
                entry = entry[k]
            except:
                return not condition
        return condition

    def _process_condition(self, operator, condition, entry):
        if isinstance(condition, Mapping) and "$exists" in condition:
            if type(operator) is str and operator.find('.') != -1:
                return self._path_exists(operator, condition['$exists'], entry)
            elif condition["$exists"] != (operator in entry):
                return False
            elif tuple(condition.keys()) == ("$exists",):
                return True
        if isinstance(operator, string_type):
            if operator.startswith("$"):
                try:
                    return getattr(self, "_" + operator[1:])(condition, entry)
                except AttributeError:
                    raise QueryError(
                        "{!r} operator isn't supported".format(operator))
                except TypeError:
                    return False
            else:
                extracted_data = self._extract(entry, operator.split("."))
        else:
            if operator not in entry:
                return False
            extracted_data = entry[operator]
        return self._match(condition, extracted_data)

    ##################
    # Common operators
    ##################

    def _not_implemented(self, *args):
        raise NotImplementedError

    def _noop(self, *args):
        return True

    ######################
    # Comparison operators
    ######################

    def _gt(self, condition, entry):
        return entry > condition

    def _gte(self, condition, entry):
        return entry >= condition

    def _in(self, condition, entry):
        return entry in condition

    def _lt(self, condition, entry):
        return entry < condition

    def _lte(self, condition, entry):
        return entry <= condition

    def _ne(self, condition, entry):
        return entry != condition

    def _nin(self, condition, entry):
        return entry not in condition

    ###################
    # Logical operators
    ###################

    def _and(self, condition, entry):
        if isinstance(condition, Sequence):
            return all(
                self._match(sub_condition, entry)
                for sub_condition in condition
            )
        raise QueryError(
            "$and has been attributed incorrect argument {!r}".format(
                condition
            )
        )

    def _nor(self, condition, entry):
        if isinstance(condition, Sequence):
            return all(
                not self._match(sub_condition, entry)
                for sub_condition in condition
            )
        raise QueryError(
            "$nor has been attributed incorrect argument {!r}".format(
                condition
            )
        )

    def _not(self, condition, entry):
        return not self._match(condition, entry)

    def _or(self, condition, entry):
        if isinstance(condition, Sequence):
            return any(
                self._match(sub_condition, entry)
                for sub_condition in condition
            )
        raise QueryError(
            "$nor has been attributed incorrect argument {!r}".format(
                condition
            )
        )

    ###################
    # Element operators
    ###################

    def _type(self, condition, entry):
        # TODO: further validation to ensure the right type
        # rather than just checking
        bson_type = {
            1: float,
            2: string_type,
            3: Mapping,
            4: Sequence,
            5: bytearray,
            7: string_type,  # object id (uuid)
            8: bool,
            9: string_type,  # date (UTC datetime)
            10: type(None),
            11: string_type,  # regex,
            13: string_type,  # Javascript
            15: string_type,  # JavaScript (with scope)
            16: int,  # 32-bit integer
            17: int,  # Timestamp
            18: int   # 64-bit integer
        }
        bson_alias = {
            "double": 1,
            "string": 2,
            "object": 3,
            "array": 4,
            "binData": 5,
            "objectId": 7,
            "bool": 8,
            "date": 9,
            "null": 10,
            "regex": 11,
            "javascript": 13,
            "javascriptWithScope": 15,
            "int": 16,
            "timestamp": 17,
            "long": 18,
        }

        if condition == "number":
            return any([
                isinstance(entry, bson_type[bson_alias[alias]])
                for alias in ["double", "int", "long"]
                ])

        # resolves bson alias, or keeps original condition value
        condition = bson_alias.get(condition, condition)

        if condition not in bson_type:
            raise QueryError(
                "$type has been used with unknown type {!r}".format(condition))

        return isinstance(entry, bson_type.get(condition))

    _exists = _noop

    ######################
    # Evaluation operators
    ######################

    def _mod(self, condition, entry):
        return entry % condition[0] == condition[1]

    def _regex(self, condition, entry):
        if not isinstance(entry, string_type):
            return False
        try:
            regex = re.match(
                "\A/(.+)/([imsx]{,4})\Z",
                condition,
                flags=re.DOTALL
            )
        except TypeError:
            raise QueryError(
                "{!r} is not a regular expression "
                "and should be a string".format(condition))

        flags = 0
        if regex:
            options = regex.group(2)
            for option in options:
                flags |= getattr(re, option.upper())
            exp = regex.group(1)
        else:
            exp = condition

        try:
            match = re.search(exp, entry, flags=flags)
        except Exception as error:
            raise QueryError(
                "{!r} failed to execute with error {!r}".format(
                    condition, error))
        return bool(match)

    _options = _text = _where = _not_implemented

    #################
    # Array operators
    #################

    def _all(self, condition, entry):
        return all(
            self._match(item, entry)
            for item in condition
        )

    def _elemMatch(self, condition, entry):
        return any(
            all(
                self._process_condition(sub_operator, sub_condition, element)
                for sub_operator, sub_condition in condition.items()
            )
            for element in entry
        )

    def _size(self, condition, entry):
        if not isinstance(condition, int):
            raise QueryError(
                "$size has been attributed incorrect argument {!r}".format(
                    condition
                )
            )

        if is_non_string_sequence(entry):
            return len(entry) == condition

        return False

    ####################
    # Comments operators
    ####################

    _comment = _noop
