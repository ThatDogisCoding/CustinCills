import sys


def main() -> None:
    from business_report.cli import main as report_main

    if len(sys.argv) > 1 and sys.argv[1] == "report":
        sys.exit(report_main(sys.argv[2:]))
    sys.exit(report_main(sys.argv[1:]))


if __name__ == "__main__":
    main()
