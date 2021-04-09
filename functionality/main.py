from handler import Handler

'''Web scraping from https://www.madbarz.com/blog'''


def main() -> None:
    executor = Handler()
    executor.check_if_database_has_data_or_is_empty()


if __name__ == "__main__":
    main()
