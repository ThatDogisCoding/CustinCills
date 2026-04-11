from dotenv import load_dotenv
from gui import TaskReporterApp


def main():
    load_dotenv()
    app = TaskReporterApp()
    app.mainloop()


if __name__ == '__main__':
    main()
