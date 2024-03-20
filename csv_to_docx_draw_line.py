"""
Created on Mon Nov 20 21:18:48 2023

@author: chiu
"""

from docx import Document
from docx.oxml.shared import OxmlElement, qn


def set_cell_edges(cell, edges, color, style, width):
    """
    Parameter   Type                 Definition
    =========== ==================== ==========================================================================================
    cell        Cell                 Cell to apply edges
    edges       str, list, None      Cell edges, options are 'top', 'bottom', 'start' and 'end'
    color       str                  Edge color
    style       str                  Edge style, options are 'single', 'dotted', 'dashed', 'dashdotted' and 'double',
    width       int, float           Edge width in points
    """
    kwargs = dict()

    for edge in edges:
        kwargs[edge] = {'sz': width, 'val': style, 'color': color}

    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # check for tag existence, if none found then create one
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    # list over all available tags
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)

            # check for tag existence, if none found, then create one
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)

            # looks like the order of attributes is important
            for key in ["sz", "val", "color", "space", "shadow"]:
                if key in edge_data:
                    element.set(qn('w:{}'.format(key)), str(edge_data[key]))

def csv_to_docx(df):

    document = Document()

    table = document.add_table(rows = df.shape[0] + 1, cols = df.shape[1])

    for i in range(df.shape[0] + 1):
        for j in range(df.shape[1]):
            if i == 0:
                table.rows[i].cells[j].text = list(df.columns)[j]
                set_cell_edges(table.rows[i].cells[j], ['top', 'bottom'], '#000000', 'single', 12)
            elif i == df.shape[0]:
                table.rows[i].cells[j].text = df.iloc[i-1, j]
                set_cell_edges(table.rows[i].cells[j], ['bottom'], '#000000', 'single', 12)
            else:
                table.rows[i].cells[j].text = df.iloc[i-1, j]

    # document.save("data/wordresult1.docx")
    return document
    
