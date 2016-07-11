#!/usr/bin/env python

import argparse

from prepare_data import main as prepare_data_main
from create_tfidf_csvmatrix_and_json import main as create_tfidf_csvmatrix_and_json_main
from create_projection import main as create_projection_main


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store', dest='dataset_folder', default='', help='Provide the dataset folder')
    parser.add_argument('-t', action='store', dest='stopword_file', default='', help='Provide the stopword text file')
    parser.add_argument('-o', action='store', dest='output_prefix', default='output', help='Provide the output prefix')
    args = parser.parse_args()

    if not args.dataset_folder:
        print "Please provide the dataset folder or a subtitle file"

    prepare_data_filename = args.output_prefix + "_prepared_data.json"
    prepare_data_main(dataset_folder=args.dataset_folder, stopword_file=args.stopword_file, output_file=prepare_data_filename)

    create_tfidf_csvmatrix_and_json_filename = args.output_prefix + "_tfidf"
    create_tfidf_csvmatrix_and_json_main(input_file=prepare_data_filename, output_file=create_tfidf_csvmatrix_and_json_filename)

    create_projection_filename = args.output_prefix + "_projection"
    create_projection_main(input_file=create_tfidf_csvmatrix_and_json_filename+"_tfidf.csv", output_file=create_projection_filename, create_data=True)
