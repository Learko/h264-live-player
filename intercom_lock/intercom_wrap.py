#!/usr/bin/env python3

import os
import sys


if __name__ == '__main__':
    try:
        while True:
            input('Waiting...')
            os.system('python3.6 intercom.py')
    except KeyboardInterrupt:
        pass
            