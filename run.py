#!/usr/bin/env python

import sys
import os
import json

sys.path.insert(0, 'src')

from etl import *

def main(targets):

    if 'etl' in targets:
        with open('config/etl-params.json') as fh:
            etl_cfg = json.load(fh)
        preprocess_data(**etl_cfg)
    return

if __name__ == "__main__":
    targets = sys.argv[1:]
    main(targets)
