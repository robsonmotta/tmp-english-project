#!/usr/bin/env python

import argparse
import datetime
import json
import copy
import chardet
import os
from os import listdir
from os.path import isfile, isdir, join
import re
import math
import nltk
# nltk.download('all')
from textblob import TextBlob as tb


def is_lower_letter(character):
    if ord(character) >= 97 and ord(character) <= 122:
        return True
    return False

def is_upper_letter(character):
    if ord(character) >= 65 and ord(character) <= 90:
        return True
    return False

def is_space_character(character):
    if ord(character) == 32:
        return True
    return False

def is_comma_character(character):
    if ord(character) == 44:
        return True
    return False

def string_has_letter(text):
    for character in list(text.lower()):
        if is_lower_letter(character):
            return True
    return False


def normalize_string(text, only_basic=False):
    text = text.replace('\n', '').replace('\r', '')
    TAG_RE = re.compile(r'<[^>]+>')
    text = TAG_RE.sub('', text)
    if only_basic:
        return text
    text = text.lower()
    final_text = ""
    for character in text:
        if is_lower_letter(character) or is_space_character(character):
            final_text += character
        else:
            final_text += " " + character + " "
    final_text = final_text.replace("  ", " ")
    return final_text


def clean_text(text, stopwords=[]):
    text = normalize_string(text)
    cleaned_text = ""
    for word in text.split():
        cleaned_word = ""
        for character in list(word):
            if is_lower_letter(character):
                cleaned_word += character
        if len(cleaned_word) <= 2:
            cleaned_text += " --- "
        elif cleaned_word in stopwords:
            cleaned_text += " --- "
        else:
            cleaned_text += cleaned_word + " "
    return cleaned_text


def list_of_subtitles(dataset_folder, subtitle_file, do_heuristic_to_avoid_duplicates=True):
    all_subtitles = []
    if dataset_folder:
        all_subtitles_folder = [ join(dataset_folder,f) for f in listdir(dataset_folder) if isdir(join(dataset_folder,f))]
        for folder in all_subtitles_folder:
            list_subtitles = [ f for f in listdir(folder) if isfile(join(folder,f)) and ".srt" in f ]
            inserted_subtitles = []
            for subtitle in list_subtitles:
                if do_heuristic_to_avoid_duplicates:
                    list_title_version_name = subtitle.split(" - ")
                    if len(list_title_version_name) < 2 or list_title_version_name[:2] in inserted_subtitles:
                        continue
                    inserted_subtitles.append(list_title_version_name[:2])
                all_subtitles.append(join(folder,subtitle))
    if subtitle_file and subtitle_file not in all_subtitles:
        all_subtitles.append(subtitle_file)
    return all_subtitles


def load_stopwords(stopword_file):
    stopwords = set()
    if not stopword_file:
        return stopwords
    with open(stopword_file, "r") as f:
        for line in f:
            words = [word.lower().decode('iso8859-1') for word in line.split()]
            for word in words:
                stopwords.add(word)
    return stopwords


# def parsetime_subtitle_time(line):
#     time_list = line.split(' --> ')
#     if len(time_list) < 2:
#         time_list_try2 = line.split('\x00-\x00-\x00>\x00')
#         if len(time_list_try2) < 2:
#             return None
#         time_list = time_list_try2 
#     parsed_time_list = []
#     for time in time_list:
#         try:
#             time_split = time.split(':')
#             if len(time_split) == 3:
#                 hours, minutes, seconds = time_split
#             else:
#                 time_split_try2 = time.split('\x00:')
#                 if len(time_split_try2) == 3:
#                     hours, minutes, seconds = time_split_try2
#             parsed_time_list.append(hours+":"+minutes+":"+seconds)
#         except:
#             return None
#     return parsed_time_list


def parsetime_subtitle_time(line):
    time_list = line.split(' --> ')
    if len(time_list) < 2:
        return None
    parsed_time_list = []
    for time in time_list:
        try:
            hours, minutes, seconds = time.split(':')
            hours = int(hours)
            minutes = int(minutes)
            seconds = float('.'.join(seconds.split(',')))
            # parsed_time_list.append(datetime.timedelta(0, seconds, 0, 0, minutes, hours))
            parsed_time_list.append(str(hours)+":"+str(minutes)+":"+str(int(seconds)))
        except:
            return None
    return parsed_time_list


def load_subtitle(subtitle):
    current_subtitle = []
    with open(subtitle, "r") as f:
        current_talk = ""
        current_start = None
        current_finish = None
        for line in f:
            time_list = parsetime_subtitle_time(line)
            if time_list:
                if current_start:
                    last_content = {
                        "start": current_start,
                        "finish": current_finish,
                        "text": normalize_string(current_talk, only_basic=True)
                    }
                    current_subtitle.append(last_content)
                current_start, current_finish = time_list
                current_talk = ""
            else:
                if string_has_letter(line):
                    current_talk += line.decode('iso8859-1') + " "
    
    return current_subtitle
    

def generate_names_set(prepared_data):
    names_set = set()
    for subtitle in prepared_data:
        for item in subtitle["original_content"]:
            text = item["text"]
            last_letter = None
            for word in text.split():
                if last_letter and is_upper_letter(word[0]) and (is_lower_letter(last_letter) or is_comma_character(last_letter)):
                    normalized_word = normalize_string(word)
                    names_set.add(normalized_word.split()[0])
                last_letter = word[-1]
    return names_set


def text_to_2gram(text):
    text_2gram = ""
    terms_list = text.split()
    if len(terms_list) < 2:
        return text_2gram
    for i, word in enumerate(terms_list[:-1]):
        word1 = terms_list[i]
        word2 = terms_list[i+1]
        if is_lower_letter(word1[0]) and is_lower_letter(word2[0]):
            text_2gram = word1+"_"+word2
    return text_2gram


def prepare_data(all_subtitles, stopwords_set):
    prepared_data = []
    for subtitle in all_subtitles:
        current_subtitle = {}
        current_subtitle["complete_path"] = subtitle
        current_subtitle["title"] = os.path.basename(subtitle)
        current_subtitle["original_content"] = load_subtitle(subtitle)
        prepared_data.append(current_subtitle)
    names_set = generate_names_set(prepared_data)
    
    stopwords_set = set(list(stopwords_set) + list(names_set))

    for subtitle in prepared_data:
        terms = []
        for item in subtitle["original_content"]:
            text = item["text"]
            filtered_text = clean_text(text, stopwords_set)
            filtered_text_2gram = text_to_2gram(filtered_text)
            terms.extend(filtered_text.replace("---", "").split())
            terms.extend(filtered_text_2gram.replace("---", "").split())
        subtitle["terms"] = terms

    return prepared_data


def save_output(output_file, prepared_data):
    with open(output_file, "w") as text_file:
        for item in prepared_data:
            if not item["terms"]:
                print "ERROR TO PROCESS (try another file):", item["title"]
                continue
            text_file.write(json.dumps(item)+"\n")    


def main(dataset_folder=None, stopword_file=None, subtitle_file=None, output_file="output.json"):

    # list of all subtitles
    all_subtitles = list_of_subtitles(dataset_folder, subtitle_file)

    # loading the stopwords
    stopwords_set = load_stopwords(stopword_file)

    # create treated output
    prepared_data = prepare_data(all_subtitles, stopwords_set)

    # save output
    save_output(output_file, prepared_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store', dest='subtitle_file', default='', help='Provide the subtitle file')
    parser.add_argument('-d', action='store', dest='dataset_folder', default='', help='Provide the dataset folder')
    parser.add_argument('-t', action='store', dest='stopword_file', default='', help='Provide the stopword text file')
    parser.add_argument('-o', action='store', dest='output_file', default='output.json', help='Provide the output file name')
    args = parser.parse_args()

    if not args.dataset_folder and not args.subtitle_file:
        print "Please provide the dataset folder or a subtitle file"

    main(dataset_folder=args.dataset_folder, stopword_file=args.stopword_file, subtitle_file=args.subtitle_file, output_file=args.output_file)
