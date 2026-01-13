# baby's first brainfuck (bf) compiler
# 
# by thomask-m
# 
# currently, it is really more like "program evaluator" rather than a compiler :P
# 
from enum import auto, Enum
import platform
import sys
from typing import List


# Prints out "Hello, World!". Bona-fide brainfuck code.
HELLO_WORLD_BF_PROG = """+++++++++++[>++++++>+++++++++>++++++++>++++>+++>+<<<<<<-]>+++
+++.>++.+++++++..+++.>>.>-.<<-.<.+++.------.--------.>>>+.>-.
"""
# TODO(1): check windows in order to handle \r\n newline breaks
IS_WINDOWS = platform.system() == "Windows"
NEWLINE_CHARS = set([
    # '\r\n', see TODO(1)
    '\n',
    '\r',
])

class Error():
    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return f"{self.message}"

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

    @classmethod
    def from_command_symbol(cls, symbol: str):
        symbol_to_action = {
            '>': Action.MOVE_RIGHT, # move the pointer to the right
            '<': Action.MOVE_LEFT, # move the pointer to the left
            '+': Action.INCREMENT, # increment the memory cell at the pointer
            '-': Action.DECREMENT, # decrement the memory cell at the pointer
            '.': Action.OUTPUT, # output the character signified by the cell at the pointer
            # TODO(2): implement input command
            ',': Action.INPUT, # input a character and store it in the cell at the pointer
            '[': Action.COND_JUMP_PAST, # jump past the matching ] if the cell at the pointer is 0
            ']': Action.COND_JUMP_BACK,  # jump back to the matching [ if the cell at the pointer is nonzero
        }
        return symbol_to_action.get(symbol, Action.NO_OP)

class ActionMetadata:
    def __init__(self, potential_goto: int):
        self.potential_goto = potential_goto

    def update_potential_goto(self, potential_goto: int):
        self.potential_goto = potential_goto

class Command:
    def __init__(self, action: Action, metadata: ActionMetadata | None):
        self.action = action
        self.metadata = metadata

    def __repr__(self):
        return f"Action: {self.action}, Metadata: {self.metadata}"

class Checker:
    @classmethod
    def has_matching_brackets(cls, program: str) -> Error | List[Command]:
        current_line_number, current_column_pos = 1, 0
        validate_matching_brackets = []
        command_index = 0
        commands = []
        for c in program:
            if c in NEWLINE_CHARS:
                current_line_number += 1
                current_column_pos = 0
            action = Action.from_command_symbol(c)
            current_column_pos += 1
            if action == Action.NO_OP:
                continue

            if action == Action.COND_JUMP_PAST:
                validate_matching_brackets.append((current_line_number, current_column_pos, command_index))
                commands.append(Command(action, ActionMetadata(-1)))
            elif action == Action.COND_JUMP_BACK:
                try:
                    _, _, right_bracket_goto = validate_matching_brackets.pop()
                    commands.append(Command(action, ActionMetadata(right_bracket_goto)))
                    command_to_update = commands[right_bracket_goto]
                    left_bracket_metadata = command_to_update.metadata
                    assert left_bracket_metadata is not None, "we should not reach this line"
                    left_bracket_metadata.update_potential_goto(command_index)
                except IndexError:
                    return Error(f"Unmatched ] error: line {current_line_number}, position: {current_column_pos}")
            else:
                commands.append(Command(action, None))
            command_index += 1
        if len(validate_matching_brackets) > 0:
            for line_num, position, _ in reversed(validate_matching_brackets):
                return Error(f"Unmatched [ error: line {line_num}, position: {position}")
        return commands

class Evaluator:
    def __init__(self, num_cells: int):
        self._num_cells = num_cells
        self._memory = [0] * self._num_cells
        self._memory_pointer = 0

    def _eval(self, command: Command, command_index: int) -> Error | int:
        """
        Takes a Command and an index, which is used to calculate the "next" index.
        """
        if command.action == Action.MOVE_RIGHT:
            self._memory_pointer += 1
            if self._memory_pointer >= self._num_cells:
                return Error(f"Memory pointer moved past the number of allocated cells set at {self._num_cells}")
        elif command.action == Action.MOVE_LEFT:
            self._memory_pointer -= 1
            if self._memory_pointer < 0:
                return Error("Memory pointer moved below zero")
        elif command.action == Action.INCREMENT:
            self._memory[self._memory_pointer] += 1
        elif command.action == Action.DECREMENT:
            self._memory[self._memory_pointer] -= 1
        elif command.action == Action.OUTPUT:
            print(chr(self._memory[self._memory_pointer]), end="")
        elif command.action == Action.INPUT:
            return Error("INPUT command not yet supported!")
        elif command.action == Action.COND_JUMP_PAST:
            if self._memory[self._memory_pointer] == 0:
                return command.metadata.potential_goto + 1
        elif command.action == Action.COND_JUMP_BACK:
            if self._memory[self._memory_pointer] != 0:
                return command.metadata.potential_goto + 1
        return command_index + 1

    def run(self, prog: List[Command]) -> Error | None:
        command_index = 0
        prog_length = len(prog)
        while command_index < prog_length:
            command = prog[command_index]
            result = self._eval(command, command_index)
            if not isinstance(result, int):
                return Error(f"Runtime error > {result}")
            command_index = result
        return None

def main():
    commands = Checker.has_matching_brackets(HELLO_WORLD_BF_PROG) 
    if not isinstance(commands, List):
        print(f"Program contains a matching brackets error:\n {commands}", file=sys.stderr)
        sys.exit(1)

    # Original implementation kept an array of size 30_000 for memory cell
    num_cells = 30_000
    result = Evaluator(num_cells).run(commands)
    if result is not None:
        print(f"Program failed:\n {result}", file=sys.stderr)


if __name__ == "__main__":
    main()

