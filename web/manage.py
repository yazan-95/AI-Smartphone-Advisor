#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    # ADD PROJECT ROOT TO PYTHON PATH
    BASE_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(BASE_DIR))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
