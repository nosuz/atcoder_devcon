#!/usr/bin/python3

# {{contents.title}}
# {{contents.url}}

# python ../validate.py {{contents.problem}}.py

# pytest tests/test_{{contents.problem | lower}}.py
# pytest tests/test_{{contents.problem | lower}}.py -k sample1

"""TEST_DATA
{% for ex in examples %}{{ex.input}}
<expected> {{ex.output}}

{% endfor -%}
"""

import os


def debug(*args):
    if os.environ.get("DEBUG") in ("1", "true", "True", "yes"):
        print(*args)


A = int(input())

A, B = input().split()

A, B = map(int, input().split())
N, M = map(int, input().split())

A = list(map(int, input().split()))
