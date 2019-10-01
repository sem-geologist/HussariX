import json
from ast import literal_eval


def interpret(string):
    """interpret any string and return casted to appropriate
    dtype python object
    """
    try:
        return literal_eval(string)
    except (ValueError, SyntaxError):
        # SyntaxError due to:
        # literal_eval have problems with strings like this '8842_80'
        return string


class ObjectifyJSONEncoder(json.JSONEncoder):
    """ JSON encoder that can handle simple lxml objectify types,
        Handles xml attributes, also returns all data types"""

    def default(self, o):
        dictionary = {}
        if hasattr(o, '__dict__') and len(o.__dict__) > 0:
            d1 = o.__dict__.copy()
            for k in d1.keys():
                if len(d1[k]) > 1:
                    d1[k] = [interpret(i.text) for i in d1[k]]
            dictionary.update(d1)
        if len(o.attrib) > 0:
            d2 = dict(o.attrib)
            for j in d2.keys():
                if j in dictionary.keys() or j == 'Type':
                    d2['XmlClass' + j] = interpret(d2[j])
                    del d2[j]
                else:
                    d2[j] = interpret(d2[j])
            dictionary.update(d2)
        if o.text is not None:
            if len(dictionary) > 0:
                dictionary.update({'value': o.pyval})
            else:
                return interpret(o.text)
        if len(dictionary) > 0:
            return dictionary


def dictionarize(xml_node):
    return json.loads(json.dumps(xml_node, cls=ObjectifyJSONEncoder)) 
