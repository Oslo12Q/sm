# -*- coding: utf-8 -*-

import json
import os
from data_clear import data_clear


if __name__ == '__main__':
    test_dir = './testdata/'
    for _, _, filenames in os.walk(test_dir):
        for filename in filenames:
            file_path = '{}/{}'.format(test_dir, filename)
            print '='*100
            _, result = data_clear(file_path)
            # print json.dumps(result, ensure_ascii=False, indent=4)
            print json.dumps(result, ensure_ascii=False)