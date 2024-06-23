#TODO: remake this so it doesn't always ask for the file maybe make this a mixin

def find_line(text: str, index: int) -> str:
    text = text.splitlines()
    return text[index - 1]

def raise_error(type: str, details: str, text: str, line_index: int, column_index: int = None, ignores_whitespace = False) -> None:
    print(find_line(text, line_index))
    ignore_alert: str = ""
    if ignores_whitespace:
        ignore_alert: str = " (ignores whitespace)" #TODO: fix this shabby workaround in the generator file, 
        #yes it ignores empty enters because it doesnt know that they are there 
    if column_index is not None:
        print("^".rjust(column_index + 1))
        print(f"{type}Error: (line {line_index} column {column_index}{ignore_alert}) {details}")
    else:
        print(f"{type}Error: (line {line_index}{ignore_alert}) {details}")
    exit(1)

