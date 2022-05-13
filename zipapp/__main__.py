"""Executable python bundle application entry point."""
import tmtrkr.server.server
import tmtrkr.models


def main():
    """Init databse and run demo server."""
    tmtrkr.models.create_all()
    tmtrkr.server.server.run(zipapp=True)


if __name__ == "__main__":
    main()
