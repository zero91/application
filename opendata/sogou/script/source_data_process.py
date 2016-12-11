#coding: utf-8
"""Transform original sohu news data from xml to csv, and tag news with its right category.
"""
import sys
import codecs
import re
from argparse import ArgumentParser

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
    for line in open(category_fname).xreadlines():
        fields = line.strip().split('\t')
        if len(fields) != 2:
            continue
        category, main_url = fields
        category_dict[main_url] = category.decode('gbk').encode('utf-8')
    return category_dict


def fetch_category(category_map, url):
    """Calculate a url's category.
    """
    for main_url, category in category_map.iteritems():
        if url.find(main_url) == 0:
            return category
    return None


def parse_args():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-i', '--input', help="Source data which need to be processed")
    arg_parser.add_argument('-c', '--category', help="File name of the category map data")
    arg_parser.add_argument('-o', '--output', help="Output training/testing data")
    return arg_parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    category_map = read_category(args.category)

    fout = open(args.output, 'w')
    with codecs.open(args.input, 'r', encoding='gb18030') as fxml:
        cnt = 0
        while True:
            input_list = list()
            for i in range(len(g_doc_match_patterns)):
                input_list.append(fxml.readline())

            end_of_file = False
            for i in range(len(input_list)):
                if len(input_list[i]) == 0:
                    end_of_file = True
                    break
            if end_of_file is True:
                break

            cnt += 6
            if cnt % 6000 == 0:
                sys.stderr.write("\rProcessing line %d" % (cnt))

            output_list = process_doc(input_list)
            category = fetch_category(category_map, output_list[0])
            if category is None:
                continue
            fout.write("%s\t%s\n" % (category, "\t".join(output_list).encode('utf-8')))

        sys.stderr.write("\rProcessing line %d\n" % (cnt))
