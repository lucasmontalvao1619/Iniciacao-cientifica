"""Entrada compartilhada dos executáveis macOS e Windows."""

import sys

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--smoke-test":
        from frontend.bundle_check import verify

        sys.exit(verify(sys.argv[2]))
    from frontend.app import main

    main()
