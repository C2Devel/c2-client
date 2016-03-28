from lxml import etree


def prettify_xml(string):
    """Returns prettified XML string."""

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.fromstring(string, parser)
    return etree.tostring(tree, pretty_print=True)
