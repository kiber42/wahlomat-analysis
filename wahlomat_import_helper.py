#!/bin/env python3

# Input file wahlomat.xml created using:
# pdf2txt.py -t xml Positionsvergleich-XYZ.pdf > wahlomat.xml

import numpy as np
from scipy.cluster.hierarchy import *
import sys
import xml.etree.ElementTree as ET

# The processing below is fragile.  Always verify the results manually.

NUM_QUESTIONS = 38

# Each symbol (Yes, No, Neutral) appears as a <curve> element with a certain number of points (pts attribute).
# However, most of the curves do not represent any of the three symbols we're interested in.
# The representation of Neutral has changed over time, it used to be a <rect> and is now a <curve> with 13 points, which is not unique.
def guess_symbol(pts_str):
    num_points = (pts_str.count(',') + 1) // 2
    if num_points == 12: # Answer: NO
        return -1
    if num_points == 6: # Answer: YES
        return +1
    raise ValueError # Neutral or not an answer


def get_bbox(element):
    try:
        bbox_str = element.attrib["bbox"]
        return tuple(float(val) for val in bbox_str.split(','))
    except KeyError:
        return None


def center(bbox):
    return 0.5 * (bbox[0] + bbox[2]), 0.5 * (bbox[1] + bbox[3])


def merge_nearby(input_list, min_distance=10):
    merged = []
    for value in sorted(input_list):
        if not merged or value - merged[-1] >= min_distance:
            merged.append(value)
    return merged


# Return lists of x and y positions that separate the answers
def get_answer_grid(page_element):
    x_sep, y_sep = [], []
    for element in list(page_element.iter('rect')):
        bbox = get_bbox(element)
        # The neutral symbol in older pdf's is created using a small rect.
        if bbox is None or bbox[0] < 400 or bbox[2] - bbox[0] < 10:
            continue
        x_sep.append(bbox[0])
        x_sep.append(bbox[2])
        y_sep.append(-bbox[1])
        y_sep.append(-bbox[3])
    # Merge nearby entries
    x_sep = merge_nearby(x_sep)
    y_sep = merge_nearby(y_sep)
    # Drop first y separator, it corresponds to the party symbols at top of page
    return x_sep, y_sep[2:]


def get_index(value, separators):
    for index in range(len(separators)):
        if value < separators[index]:
            return index - 1
    return len(separators) - 1


# Process all <curve> elements on a page and extract all symbols representing answers
def locate_answers(curves, x_sep, y_sep):
    items = {}
    for curve in curves:
        try:
            answer = guess_symbol(curve.get('pts'))
        except ValueError:
            continue
        center_x, center_y = center(get_bbox(curve))
        pos_x = get_index(center_x, x_sep)
        pos_y = get_index(-center_y, y_sep)
        items[(pos_x, pos_y)] = answer
    return items


def extract_answers_from_xml(filename):
    tree = ET.parse(filename).getroot()
    all_answers = []
    for page in tree.iter('page'):
        curve_data = page.iter('curve')
        x_sep, y_sep = get_answer_grid(page)
        answers = locate_answers(curve_data, x_sep, y_sep)
        num_parties = max(x for (x, y) in answers.keys()) + 1
        all_answers.extend([answers.get((i_party, i_question), 0) for i_question in range(NUM_QUESTIONS)] for i_party in range(num_parties))
    return all_answers


def print_answers(all_answers):
    for answers in all_answers:
        line = "   answers: [" + ", ".join("{:+1}".format(answer) for answer in answers)
        print(line.replace("+0", " 0") + "]")


def determine_orderings(all_answers):
    for mode in ['weighted', 'single', 'complete']:
        L = linkage(np.array(all_answers), mode, 'correlation')
        order = dendrogram(L, color_threshold=0)['leaves']
        print("order:", order, "#", mode)


if __name__ == "__main__":
    all_answers = extract_answers_from_xml(sys.argv[1] if len(sys.argv) > 1 else "wahlomat.xml")
    print_answers(all_answers)
    determine_orderings(all_answers)
