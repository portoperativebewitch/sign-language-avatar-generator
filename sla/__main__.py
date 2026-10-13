"""Allow `python -m sla` invocation."""
from sla.bootstrap import main

if __name__ == "__main__":
    raise SystemExit(main())