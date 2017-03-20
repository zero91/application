#coding: utf-8
import sys
import os
import random
import argparse
import collections

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input filename of all training/testing data.")
    parser.add_argument("--ratio", default="7:1:2", help="Train:Validate:Test number ratio.")
    parser.add_argument("--seed", default=997, type=int, help="Train:Validate:Test number ratio.")
    parser.add_argument("-o", "--output_path", help="Output path of all split data")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    ftrain = open("{0}/train".format(args.output_path), 'w')
    fvalid = open("{0}/validate".format(args.output_path), 'w')
    ftest = open("{0}/test".format(args.output_path), 'w')

    ratio_list = map(float, args.ratio.split(':'))
    if len(ratio_list) != 3:
        raise ValueError("Argument `ratio` should be three columns separated by a colon.")

    train_ratio_end = ratio_list[0] / sum(ratio_list)
    validate_ratio_end = sum(ratio_list[0:2]) / sum(ratio_list)
    test_ratio_end = 1.0

    random.seed(args.seed)

    category_set = set()
    stat = { "train" : collections.defaultdict(int),
             "test" : collections.defaultdict(int),
             "validate" : collections.defaultdict(int) }
    for line in open(args.input, 'r').xreadlines():
        category, url, docno, title, content = line[:-1].split('\t')
        category_set.add(category)
        rand_val = random.random()
        if 0 <= rand_val <= train_ratio_end:
            stat['train'][category] += 1
            ftrain.write("{0}\t{1}\t{2}\t{3}\n".format(category, docno, title, content))

        elif train_ratio_end < rand_val <= validate_ratio_end:
            stat['validate'][category] += 1
            fvalid.write("{0}\t{1}\t{2}\t{3}\n".format(category, docno, title, content))

        elif validate_ratio_end < rand_val <= 1.0:
            stat['test'][category] += 1
            ftest.write("{0}\t{1}\t{2}\t{3}\n".format(category, docno, title, content))

    sys.stdout.write("        train  validate  test\n")
    for category in category_set:
        sys.stdout.write("%s\t%-5d  %-8d  %-4d\n" % (category.decode("gbk").encode('utf-8'),
                stat['train'][category], stat['validate'][category], stat['test'][category]))

    sys.stdout.write("total\t%-5d  %-8d  %-4d\n" % (sum(stat['train'].values()),
                sum(stat['validate'].values()), sum(stat['test'].values())))

