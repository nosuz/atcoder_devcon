#!/usr/bin/env python

import re
import subprocess
import os
import argparse


def parse_limit(value):
    return set(map(int, value.split(',')))


def extract_test_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    match = re.search(r'"""TEST_DATA(.*?)"""', content, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None


def run_prog_with_data(prog_name, data, debug=False):
    blocks = data.strip().split("\n\n")  # Split into blocks by empty lines
    for index, block in enumerate(blocks):
        # skip not specified sample
        if args.limit and not index in [i - 1 for i in args.limit]:
            continue

        try:
            input_data, expected_answer = block.split("<expected>")
            expected_answer = expected_answer.strip().replace('\n', ' ')
        except ValueError:
            input_data = block
            expected_answer = None
        print(f"Input {index + 1}")
        print(input_data)

        env = os.environ.copy()
        if debug:
            env['DEBUG'] = '1'
        process = subprocess.Popen(["python3", prog_name], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        stdout, stderr = process.communicate(input=input_data)
        stdout = stdout.strip().replace('\n', ' ')
        print(f"Output {index + 1}")
        print(stdout, stderr)
        if process.returncode != 0:
            break
        elif expected_answer:
            if stdout == expected_answer:
                print("✅ OK")
            else:
                print(f"❌ WA, expected: {expected_answer}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=parse_limit,
                        help='limit validation sample. --limit 1,2,3')
    parser.add_argument('--debug', action='store_true',
                        help='set DEBUG=1 in subprocess')
    parser.add_argument('filename', help='target code file')

    args = parser.parse_args()

    # filename = sys.argv[1]
    extracted_data = extract_test_data(args.filename)
    if extracted_data is not None:
        # Use filename as program name
        run_prog_with_data(args.filename, extracted_data, args.debug)
    else:
        print("TEST_DATA not found.")
