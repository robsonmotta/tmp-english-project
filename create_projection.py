#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.manifold import TSNE
from sklearn.manifold import Isomap
from sklearn.decomposition import PCA
from sklearn.decomposition import RandomizedPCA
from sklearn.decomposition import TruncatedSVD

import argparse
import json

def main(input_file=None, output_file="output", create_data=False):

    if create_data:
        fh_X = open(output_file+"_X.txt", 'wb')
        fh_labels = open(output_file+"_labels.txt", 'wb')
        fh_labelsnames = open(output_file+"_labelsnames.txt", 'wb')
        label_dict = {}
        counter = -1
        with open(input_file, "r") as f:
            for line in f:
                data = line.split(",")

                if counter < 0:
                    counter += 1
                    continue

                label = data[-1]
                if label not in label_dict:
                    label_dict[label] = counter
                    counter += 1
                fh_labels.write(str(label_dict[label]) + "\n")
                fh_labelsnames.write(label + "\n")

                line_to_insert = ' '.join(data[1:-1])
                fh_X.write(line_to_insert + "\n")

        fh_X.close()
        fh_labels.close()
        fh_labelsnames.close()

        X = np.loadtxt(output_file+"_X.txt")

        print "TruncatedSVD"
        svd = TruncatedSVD(n_components=50, random_state=42)
        svd.fit(X)
        X = svd.transform(X)

        print "TSNE"
        tsne = TSNE(n_components=2, random_state=0, metric="cosine")
        Y = tsne.fit_transform(X)

        np.savetxt(output_file+"_Y.txt", Y)

    print "Creating the projection:"

    Y = np.loadtxt(output_file+"_Y.txt")
    labels = np.loadtxt(output_file+"_labels.txt")
    axys_labelnames = []
    with open(output_file+"_labelsnames.txt", "r") as f:
        for line in f:
            label = line.replace("\n", "")
            if label:
                axys_labelnames.append(label)

    dict_points = {}
    for pair, label in zip(Y, axys_labelnames):
        dict_points.setdefault(label, {})
        dict_points[label].setdefault("X", [])
        dict_points[label].setdefault("Y", [])
        dict_points[label]["X"].append(pair[0])
        dict_points[label]["Y"].append(pair[1])

    fh_json = open(output_file+"_projection.json", 'wb')
    for label in dict_points:
        list_x = dict_points[label]["X"]
        list_y = dict_points[label]["Y"]
        for x, y in zip(list_x, list_y):
            output_json = {
                "X": x,
                "Y": y,
                "label": label,
            }
            fh_json.write(json.dumps(output_json) + "\n")
    fh_json.close()

    list_point_group = []
    list_labels = []
    colors = iter(cm.rainbow(np.linspace(0, 1, len(dict_points))))
    for label in dict_points:
        list_labels.append(label)
        point_group = plt.scatter(dict_points[label]["X"], dict_points[label]["Y"], color=next(colors))
        list_point_group.append(point_group)

    plt.legend(
        list_point_group,
        list_labels,
        scatterpoints=1,
        loc='lower right',
        ncol=3,
        fontsize=8
    )

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action='store', dest='input_file', default='', help='Provide the csv matrix input file')
    parser.add_argument('-o', action='store', dest='output_file', default='output.json', help='Provide the output file name')
    parser.add_argument('-c', action='store', dest='create_data', default=False, help='Provide the output file name')
    args = parser.parse_args()

    if not args.input_file:
        print "Please provide the input_file"

    main(input_file=args.input_file, output_file=args.output_file, create_data=args.create_data)
