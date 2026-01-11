# baby's first brainfuck (bf) compiler
#
from enum import auto, Enum
import platform
import sys
from typing import List, Optional

class Action(Enum):
    NO_OP = auto()
    MOVE_RIGHT = auto()
    MOVE_LEFT = auto()
    INCREMENT = auto()
    DECREMENT = auto()
    OUTPUT = auto()
    INPUT = auto()
    COND_JUMP_PAST = auto()
    COND_JUMP_BACK = auto()

BF_TOKENS = {
    '>': Action.MOVE_RIGHT, # move the pointer to the right
    '<': Action.MOVE_LEFT, # move the pointer to the left
    '+': Action.INCREMENT, # increment the memory cell at the pointer
    '-': Action.DECREMENT, # decrement the memory cell at the pointer
    '.': Action.OUTPUT, # output the character signified by the cell at the pointer
    ',': Action.INPUT, # input a character and store it in the cell at the pointer
    '[': Action.COND_JUMP_PAST, # jump past the matching ] if the cell at the pointer is 0
    ']': Action.COND_JUMP_BACK,  # jump back to the mathing [ if the cell at the pointer is nonzero
}

NEWLINE_CHARS = set([
    # '\r\n', see TODO(1)
    '\n',
    '\r',
])

HELLO_WORLD_BF_PROG = """+++++++++++[>++++++>+++++++++>++++++++>++++>+++>+<<<<<<-]>+++
+++.>++.+++++++..+++.>>.>-.<<-.<.+++.------.--------.>>>+.>-.
"""

# Original implementation kept an array of size 30_000 for memory cell
MEMORY_CELL = [0] * 30_000

# TODO(1): check windows in order to handle \r\n newline breaks
IS_WINDOWS = platform.system() == "Windows"

def tokenize(c: str) -> Action:
    return BF_TOKENS.get(c, Action.NO_OP)

def program_has_matching_brackets(prog: str) -> Optional[List[Action]]:
    current_line_number, current_column_pos = 1, 0
    validate_matching_brackets = []
    actions = []
    for c in prog:
        if c in NEWLINE_CHARS:
            current_line_number += 1
            current_column_pos = 0
        action = tokenize(c)
        current_column_pos += 1
        if action == Action.NO_OP:
            continue

        if action == Action.COND_JUMP_PAST:
            validate_matching_brackets.append((current_line_number, current_column_pos))
        if action == Action.COND_JUMP_BACK:
            try:
                validate_matching_brackets.pop()
            except IndexError:
                print(f"Unmatched ] error: line {current_line_number}, position: {current_column_pos}", file=sys.stderr)
                return None
        actions.append(action)
    if len(validate_matching_brackets) > 0:
        for unmatched_bracket_data in reversed(validate_matching_brackets):
            line_num, position = unmatched_bracket_data
            print(f"Unmatched [ error: line {line_num}, position: {position}", file=sys.stderr)
            return None
    return actions

def main():
    actions = program_has_matching_brackets(HELLO_WORLD_BF_PROG) 
    assert actions is not None, "Program contains a syntax error"

    assert 1 == 0, "Delete me once I'm implemented"

if __name__ == "__main__":
    main()

