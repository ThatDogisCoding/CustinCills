import sys


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        from business_report.cli import main as report_main

        sys.exit(report_main(sys.argv[2:]))
    if len(sys.argv) > 1 and sys.argv[1] == "legacy":
        from task_reporter import main as legacy_main

        legacy_main()
        return

    from business_report.ui.app import run_app

    run_app()


if __name__ == "__main__":
    main()
