import defusedxml.ElementTree as dxml
import yldprolog.engine
from yldprolog.engine import get_value, to_python, unify, Atom, Variable

def load_xml_tree(xml_tree, filename):
    # first, filename must be bound to an Atom.
    fn_a = get_value(filename)
    if not isinstance(fn_a, Atom):
        # we could raise an exception, but we will just return and not
        # yield any results
        return
    with open(to_python(fn_a), 'r') as f:
        tree = dxml.parse(f)
        a = Atom(tree)
        for r in unify(xml_tree, a):
            yield False

def get_xpath_value(xml_tree, query, variable):
    '''xpath(Tree, Query, Variable).
    runs the xpath query Query against the XML tree Tree, and
    stores its result in Variable.'''
    # check if tree and query are bound to a value
    tree_a = get_value(xml_tree)
    if not isinstance(tree_a, Atom):
        return
    query_a = get_value(query)
    if not isinstance(query, Atom):
        return
    # do the XPath query
    root = to_python(tree_a).getroot()
    q = to_python(query_a)
    for v in root.findall(q):
        for r in unify(variable, Atom(v)):
            yield False

qe = yldprolog.engine.YP()
qe.register_function('xml_tree', load_xml_tree)
qe.register_function('xpath', get_xpath_value)

# Execute xml_tree(Tree, 'books.xml').
fn_a = qe.atom('books.xml')
v = qe.variable()
tree_a = [ get_value(v) for r in qe.query('xml_tree', [ v, fn_a ])][0]

# Execute xpath(Tree, 'book/author', V).
q_a = qe.atom('book/author')
authors = [ to_python(v) for r in qe.query('xpath', [ tree_a, q_a, v ])]
for a in authors:
    print(a.text)


