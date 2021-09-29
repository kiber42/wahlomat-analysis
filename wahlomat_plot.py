#!/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import yaml

plt.rcParams['font.size'] = 4
plt.rcParams.update(
    {'figure.titlesize': 18, 'xtick.labelsize': 6, 'ytick.labelsize': 6})


def plot(scores, names, vmin, vmax, formatter=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(scores, vmin=vmin, vmax=vmax, cmap='jet')
    fig.colorbar(cax)
    n = len(names)
    ticks = np.arange(n)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(names, rotation=90)
    ax.set_yticklabels(names)
    if formatter is not None:
        for x in range(len(names)):
            for y in range(len(names)):
                ax.annotate(formatter(scores[x][y]), xy=(
                    x, y), ha="center", va="center")


def get_score(answers1, answers2):
    n_both_neutral = np.count_nonzero((answers1 == 0) & (answers2 == 0))
    return (np.sum(np.abs(answers1 + answers2)) / 2 + n_both_neutral) * 100 / len(answers1)


def compute_wahlomat_scores(all_answers):
    n = len(all_answers)
    scores = 100 * np.eye(n)
    for i in range(n):
        for j in range(i):
            scores[i, j] = scores[j, i] = get_score(
                all_answers[i], all_answers[j])
    return scores


def layout_and_save(title, filename="plot.png"):
    plt.gcf().suptitle(title)
    plt.tight_layout()
    # tight layout does not leave room for title!
    plt.subplots_adjust(top=0.8)
    plt.draw()
    plt.savefig(fname=filename, dpi=300)


def determine_ordering(all_answers, mode):
    if mode is None:
        mode = "weighted"
    from scipy.cluster.hierarchy import dendrogram, linkage
    L = linkage(np.array(all_answers), mode, 'correlation')
    return dendrogram(L, color_threshold=0, no_plot=True)['leaves']


def strip_extension(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def process(filename, ordering=None):
    data = open(filename, encoding="utf-8")
    doc = yaml.full_load(data)
    title = "Wahl-O-Mat " + doc["title"]
    parties = doc["parties"]
    names = [party["short"] for party in parties]
    all_answers = [party["answers"] for party in parties]
    if not ordering and "order" in doc:
        order = doc['order']
    else:
        order = determine_ordering(all_answers, ordering)
    names_ordered = [names[i] for i in order]
    all_answers_ordered = np.array(all_answers)[order, :]
    corr = np.corrcoef(all_answers_ordered)
    scores = compute_wahlomat_scores(all_answers_ordered)
    plot(corr, names_ordered, None, +1,
         formatter=lambda val: "{:.0f}".format(val*100))
    filename = strip_extension(filename)
    os.makedirs("plots", exist_ok=True)
    layout_and_save(title, os.path.join(
        "plots", "wahlomat_correlations_" + filename + ".png"))
    plot(scores, names_ordered, None, 100,
         formatter=lambda val: "{:.0f}".format(val))
    layout_and_save(title, os.path.join(
        "plots", "wahlomat_scores_" + filename + ".png"))


if __name__ == "__main__":
    filenames = sys.argv[1:] if len(sys.argv) > 1 else ["bundestag2021.yaml"]
    for filename in filenames:
        if len(filenames) > 1:
            print("Processing " + filename)
        process(filename)
    plt.show()
