from comptypes import Token

class ErrorHandler:
    file_path: str = "" 
    dialect_errors: bool = False
    debug_mode: bool = False

    translate: dict[str, str] = {
        "Syntax": "NapisanePlano",
        "Value": "HodnotaPlana",
        "Generator": "VyrobaPlana",
        "Parsing": "DzelenePlane",
        "Type": "TypPlany",
        }
    
    def __init__(self, file: str) -> None:
        self.file_content: str = file
        self.line_number: int = 1
        self.column_number: int = 0

    def get_error_line(self) -> str:
        """
        returns the line where the error happened based on the line number
        """
        file_content = self.file_content.splitlines()
        return file_content[self.line_number - 1] if self.line_number - 1 < len(file_content) else file_content[-1]

    def compiler_error(self, type_: str, details: str, line_and_num: Token | tuple[int, int] | None = None) -> None:
        """
        throws an error based on the given type, details and location passed in,
        if the location isn't given then it assumes the line and column
        """
        if isinstance(line_and_num, Token):
            self.line_number = line_and_num.line
            self.column_number = line_and_num.col
        elif line_and_num:
            self.line_number, self.column_number = line_and_num
        
        error_line = self.get_error_line()
        print(f"Failed here: {self.file_path}:{self.line_number}:{self.column_number}")
        print(error_line)
        
        if line_and_num:
            print("^".rjust(self.column_number))
            col_report = \
            f" column {self.column_number}" if not self.dialect_errors \
            else f" stlupik {self.column_number}"
        else:
            print("^" * len(error_line))
            col_report = ""
        
        if not self.dialect_errors:
            print(f"{"\033[31m"}{type_}Error{"\033[0m"}: (line {self.line_number}{col_report}) {details}")
        else:
            print(f"Joj bysťu {"\033[31m"}{self.translate[type_]}{"\033[0m"}: (lajna {self.line_number}{col_report}) {details}")
        exit(1)
