
class ErrorHandler:
    def __init__(self, file: str) -> None:
        self.file_content: str = file
        self.line_number: int = 1
        self.column_number: int = -1

    def find_line(self) -> str:
        file_content = self.file_content.splitlines()
        return file_content[self.line_number - 1]

    def raise_error(self, type: str, details: str, ignores_whitespace = False) -> None:
        wrong_line = self.find_line()
        print(wrong_line)
        ignore_alert: str = ""
        if ignores_whitespace:
            ignore_alert: str = " (ignores whitespace)" #TODO: fix this shabby workaround in the generator file, 
            #yes it ignores empty enters because it doesn't know that they are there 
        if self.column_number != -1:
            print("^".rjust(self.column_number + 1))
            print(f"{type}Error: (line {self.line_number} column {self.column_number}{ignore_alert}) {details}")
        else:
            print("^" * len(wrong_line))
            print(f"{type}Error: (line {self.line_number}{ignore_alert}) {details}")
        exit(1)
