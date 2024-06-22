
def find_line(text: str, index: int) -> str:
    text = text.splitlines()
    return text[index - 1]

def raise_error(type: str, details: str, text: str, line_index: int, column_index: int = None) -> None:
    print(find_line(text, line_index))
    if column_index is not None:
        print("^".rjust(column_index + 1))
    print(f"{type}Error: (line {line_index} column {column_index}) {details}")
    exit(1)

