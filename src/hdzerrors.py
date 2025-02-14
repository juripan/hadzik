from comptypes import Token

class ErrorHandler:
    dialect_errors: bool = False
    translate: dict[str, str] = {"Syntax": "NapisanePlano", "Value": "HodnotaPlana", "Generator": "VyrobaPlana", "expected": "tu malo buc toto", "Parsing": "DzelenePlane"}
    def __init__(self, file: str) -> None:
        self.file_content: str = file
        self.line_number: int = 1
        self.column_number: int = 0

    def find_line(self) -> str:
        file_content = self.file_content.splitlines()
        return file_content[self.line_number - 1] if self.line_number - 1 < len(file_content) else file_content[-1]

    def raise_error(self, type: str, details: str, curr_token: Token | None = None) -> None:
        if curr_token:
            self.line_number = curr_token.line
            self.column_number = curr_token.col
        
        error_line = self.find_line()
        print(error_line)
        if self.column_number != -1:
            print("^".rjust(self.column_number))
            print(f"{"\033[31m"}{type}Error{"\033[0m"}: (line {self.line_number} column {self.column_number}) {details}" 
                    if not self.dialect_errors else f"Joj bysťu {"\033[31m"}{self.translate[type]}{"\033[0m"}: (lajna {self.line_number} stlupik {self.column_number}) {details}")
        else:
            print("^" * len(error_line))
            print(f"{"\033[31m"}{type}Error{"\033[0m"}: (line {self.line_number}) {details}" if
                    not self.dialect_errors else f"Joj bysťu {self.translate[type]}: (lajna {self.line_number}) {details}")
        exit(1)
