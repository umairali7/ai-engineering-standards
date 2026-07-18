"""Enable `python -m aies` as an alias for the `aies` console entry point."""

import sys

from .cli import main

if __name__ == "__main__":
    # Propagate the CLI's return code as the process exit status, so
    # `python -m aies … --gate` fails the shell exactly like the console script.
    sys.exit(main())
