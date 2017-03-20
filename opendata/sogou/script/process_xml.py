#coding: utf-8
"""Transform original sohu news data from xml to csv, and tag news with its right category.
"""
import sys
import os
import codecs
import re
from argparse import ArgumentParser

CURRENT_SCRIPT_PATH, CURRENT_SCRIPT_FNAME = os.path.split(os.path.realpath(__file__))

g_doc_match_patterns = [
            (re.compile(r'<doc>'), False), # format: pattern, 是否取出匹配到的数据
            (re.compile(r'<url>(.*)</url>'), True),
            (re.compile(r'<docno>(.*)</docno>'), True),
            (re.compile(r'<contenttitle>(.*)</contenttitle>'), True),
            (re.compile(r'<content>(.*)</content>'), True),
            (re.compile(r'</doc>'), False),
        ]

def process_doc(input_list):
    """Fetch the input xml format data.
    """
    if len(input_list) != len(g_doc_match_patterns):
        return None

    ret_val = list()
    for i, (p, used) in enumerate(g_doc_match_patterns):
        match_obj = p.match(input_list[i])
        if not match_obj:
            sys.stderr.write("Pattern [%s] not matched for [%s]\n" % (p.pattern, input_list[i]))
            return None
        if used:
            ret_val.append(match_obj.group(1))
    return ret_val


def read_category(category_fname):
    """Read input category file and tranformed it into a map.
    """
    category_dict = dict()
    for line in open(category_fname, 'r').xreadlines():
        fields = line.strip().split('\t')
        if len(fields) != 2:
            continue
        category, main_url = fields
        category_dict[main_url] = category
    return category_dict


def fetch_category(category_map, url):
    """Calculate a url's category.
    """
    for main_url, category in category_map.iteritems():
        if url.startswith(main_url):
            return category
    return None


def main():
    args = parse_args()
    category_map = read_category("{0}/../data_in/categories_2012.txt".format(CURRENT_SCRIPT_PATH))
    if args.output is None:
        fout = sys.stdout
    else:
        fout = open(args.output, 'w')
    with codecs.open("{0}/../data_in/news_sohusite_xml.dat".format(
                        CURRENT_SCRIPT_PATH), 'r') as fxml:
        line_cnt = 0
        while True:
            input_list = list()
            for i in range(len(g_doc_match_patterns)):
                input_list.append(fxml.readline())

            end_of_file = False
            for line in input_list:
                if len(line) == 0:
                    end_of_file = True
                    break
            if end_of_file is True:
                break

            line_cnt += 6
            if line_cnt % 6000 == 0:
                sys.stderr.write("\rProcessing doc %dk" % (line_cnt / 6000))

            output_list = process_doc(input_list)
            category = fetch_category(category_map, output_list[0])
            if category is None:
                continue
            fout.write("%s\t%s\n" % (category, "\t".join(output_list)))
        sys.stderr.write("\rProcessing doc %dk\n" % (line_cnt / 6000))


def parse_args():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-o', '--output', help="Output training/testing data")
    return arg_parser.parse_args()

if __name__ == '__main__':
    main()
