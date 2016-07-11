#!/usr/bin/env python

import argparse
import json
import math
from prepare_data import clean_text

def tfidf(word, terms_count, subtitles_terms_count, subtitles_terms_occourrences):
    tf = terms_count.get(word, 0) / float(len(terms_count))
    n_containing = subtitles_terms_occourrences.get(word, 0)
    idf = math.log(len(subtitles_terms_count) / float(1 + n_containing))
    return tf * idf


def get_number_of_subtitles_per_term(subtitles_terms_count, valid_terms):
    subtitles_terms_occourrences = {}
    for terms_count in subtitles_terms_count:
        for term in terms_count:
            subtitles_terms_occourrences.setdefault(term, 0)
            subtitles_terms_occourrences[term] += 1
    return subtitles_terms_occourrences

def save_matrix_csv(matrix_list, all_terms, field_to_get, output_file):
    with open(output_file+".csv", "w") as text_file:
        csv_output = 'title'
        csv_output += ','
        csv_output += ','.join(all_terms)
        csv_output += ','
        csv_output += 'class'
        text_file.write(csv_output+"\n")
        for item in matrix_list:
            csv_output = item["title"]
            csv_output += ','
            csv_output += ','.join([str(item[field_to_get].get(term, 0)) for term in all_terms])
            csv_output += ','
            csv_output += item["class"]
            text_file.write(csv_output+"\n")    


def get_valid_terms(input_file):
    print "getting valid terms (more than 1 occourrences)"
    all_terms = set()
    all_terms_more_than_one = set()
    with open(input_file, "r") as f:
        for line in f:
            data = json.loads(line)
            for term in data.get("terms", []):
                if term in all_terms:
                    all_terms_more_than_one.add(term)
                else:
                    all_terms.add(term)
    print "# valid terms:", len(all_terms_more_than_one)
    return all_terms_more_than_one

def prepare_data(input_file, valid_terms):
    print "preparing data to generate tfidf"
    subtitles_title_and_termscount = []
    with open(input_file, "r") as f:
        for line in f:
            data = json.loads(line)
            title = data["title"]
            terms_count = {}
            for term in data.get("terms", []):
                if term not in valid_terms:
                    continue
                terms_count.setdefault(term, 0)
                terms_count[term] += 1
            examples_phrases = {}
            for item in data["original_content"]:
                original_phrase = item["text"]
                treated_phrase = clean_text(item["text"])
                for term in terms_count:
                    if term.replace("_", " ") in treated_phrase:
                        examples_phrases.setdefault(term, [])
                        examples_phrases[term].append(original_phrase)
            subtitles_title_and_termscount.append((title, terms_count, examples_phrases))

    print "# valid subtitles:", len(subtitles_title_and_termscount)
    return subtitles_title_and_termscount

def get_tfidf_matrix_item(title, terms_count, all_classes, valid_terms, subtitles_terms_count, subtitles_terms_occourrences):
    tfidf_matrix_item = {}
    tfidf_matrix_item["title"] = title
    current_class = title.split(" - ")[0]
    tfidf_matrix_item["class"] = current_class
    if current_class not in all_classes:
        print "processing:", current_class
        all_classes.append(current_class)
    tfidf_matrix_item["terms_count"] = terms_count
    scores = {word: tfidf(word, terms_count, subtitles_terms_count, subtitles_terms_occourrences) for word in terms_count}
    tfidf_matrix_item["terms_tfidf"] = {}
    for word in scores:
        tfidf_matrix_item["terms_tfidf"][word] = scores[word]
    return tfidf_matrix_item, scores

def get_examples_per_subtitle_list(title, terms_count, scores, subtitles_dict):
    top_n = 10
    min_freq = 2
    top_examples = 5
    sorted_words_by_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    count_tfidf = 0
    output_list = []
    for word, score in sorted_words_by_scores:
        if count_tfidf > top_n:
            break
        count_tfidf += 1
        if terms_count[word] < min_freq:
            continue
        examples = [line for line in subtitles_dict[word][:top_examples]]
        item_to_add = {
            "term": word,
            "tfidf": round(scores[word],3),
            "freq": terms_count[word],
            "phrases": examples,
        }
        output_list.append(item_to_add)
    return {"title": title, "examples": output_list}

def main(input_file=None, output_file="output"):

    valid_terms = get_valid_terms(input_file)
    subtitles_title_and_termscount = prepare_data(input_file, valid_terms)

    print "preparing to calc frequence and tfidf value"
    matrix_list = [] 
    examples_per_subtitle_list = [] 
    subtitles_terms_count = [terms_count for _, terms_count, _ in subtitles_title_and_termscount]
    subtitles_terms_occourrences = get_number_of_subtitles_per_term(subtitles_terms_count, valid_terms)
    all_classes = []
    print "generating frequence and tfidf value"
    for title, terms_count, examples_phrases in subtitles_title_and_termscount:
        matrix_list_item, scores = get_tfidf_matrix_item(title, terms_count, all_classes, valid_terms, subtitles_terms_count, subtitles_terms_occourrences)
        matrix_list.append(matrix_list_item)
        examples_per_subtitle_item = get_examples_per_subtitle_list(title, terms_count, scores, examples_phrases)
        examples_per_subtitle_list.append(examples_per_subtitle_item)
        
    print "saving frequence csv"
    save_matrix_csv(matrix_list, valid_terms, "terms_count", output_file+"_freq")
    print "saving tfidf csv"
    save_matrix_csv(matrix_list, valid_terms, "terms_tfidf", output_file+"_tfidf")
    print "saving terms to study in json"
    with open(output_file+"_to_study_english.json", "w") as text_file:
        for item in examples_per_subtitle_list:
            text_file.write(json.dumps(item)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', action='store', dest='input_file', default='', help='Provide the prepared_data json input file')
    parser.add_argument('-o', action='store', dest='output_file', default='output.json', help='Provide the tfidf_matrix csv output file name')
    args = parser.parse_args()

    if not args.input_file:
        print "Please provide the input_file"

    main(input_file=args.input_file, output_file=args.output_file)
