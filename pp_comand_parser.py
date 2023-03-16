

import re


def parse(pp_command: str) -> tuple[set, dict, str, set, dict, list]:
    '''
    Parse command string and return command information
    Returns:
        (general_flags: set, general_options: dict, command: str, command_flags: set, command_options: dict, others: list)        
    '''
    args = pp_command.split()

    command = ""
    general_flags = set()
    general_options = {}

    command_flags = set()
    command_options = {}
    others = []

    index = 0
    flags = general_flags
    options = general_options
    while index < len(args):
        arg = args[index]

        if arg == '/pp':
            index += 1
            continue

        if arg.startswith('--'):
            flags.add(arg)
            index += 1

        elif arg[0] == '-':
            if index + 1 >= len(args):
                return f"please provide input value for '{arg}'"

            value = args[index + 1]

            if value[0] == '-':
                return f"please provide input value for '{arg}'"

            options[arg] = value
            index += 2

        elif command == '':
            command = arg
            options = command_options
            index += 1

        else:
            others.append(arg)
            index += 1

    return (general_flags, general_options, command, command_flags, command_options, others)
