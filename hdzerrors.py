
class ErrorHandler:
    def __init__(self, file: str) -> None:
        self.file_content: str = file
        self.line_number: int = 1
        self.column_number: int = 0

    def find_line(self) -> str:
        file_content = self.file_content.splitlines()
        return file_content[self.line_number - 1] if self.line_number - 1 < len(file_content) else file_content[-1]

    def raise_error(self, type: str, details: str) -> None:
        wrong_line = self.find_line()
        print(wrong_line)
        if self.column_number != -1:
            print("^".rjust(self.column_number))
            print(f"{type}Error: (line {self.line_number} column {self.column_number}) {details}")
        else:
            print("^" * len(wrong_line))
            print(f"{type}Error: (line {self.line_number}) {details}")
        exit(1)
