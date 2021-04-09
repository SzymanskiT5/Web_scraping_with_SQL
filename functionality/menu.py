import pyinputplus as pyip


class Menu:
    def __init__(self, **kwargs):
        self.options = {}
        for name, func in kwargs.items():
            name = name.replace("_", " ")
            name = name.capitalize()
            self.options.update({name: func})

    def execute_menu(self) -> None:
        user_choice = pyip.inputMenu(["Check for updates",
                                      "Show authors",
                                      "Show all content from all authors",
                                      "Show all content from one author",
                                      "Show articles sorted by adding date",
                                      "Show articles selected from date",
                                      "Show articles selected from category",
                                      "Delete all"],
                                     "What would you like to do?\n",
                                     numbered=True)

        self.options.get(user_choice, self.not_valid)()

    def not_valid(self) -> None:
        print("Wrong choice!")
