import os
import sys
import argparse
from jpyutils import runner

CURRENT_SCRIPT_PATH, CURRENT_SCRIPT_FNAME = os.path.split(os.path.realpath(__file__))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_dir", help="Output data path.")
    parser.add_argument("-r", "--run", nargs='?', help="Running jobs.")
    parser.add_argument("-l", "--list", action="store_true", help="List all jobs.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    tasks_runner = runner.MultiTaskRunner()
    tasks_runner.add(["python", "{0}/process_xml.py".format(CURRENT_SCRIPT_PATH),
                                "-o", "{0}/../data_in/train_test.all".format(CURRENT_SCRIPT_PATH)
                    ],
                    name = "process_xml")
    tasks_runner.add(["python", "{0}/split_train_test.py".format(CURRENT_SCRIPT_PATH),
                                "-i", "{0}/../data_in/train_test.all".format(CURRENT_SCRIPT_PATH),
                                "-o", "{0}/../data_in".format(CURRENT_SCRIPT_PATH)
                    ],
                    depends = "process_xml",
                    name = "split_train_test")

    if args.list is True:
        tasks_runner.lists()
        exit(0)

    tasks_runner.run(args.run)
