class DomainException(Exception):
    """Domain exception"""

class TooLongTitleException(DomainException):
    def __init__(self, title: str):
        self.title = title
        super().__init__(f"Название '{title}' превышает максимальную длину 30 символов.")

