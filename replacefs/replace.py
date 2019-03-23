#!/usr/bin/python

import os
import re
import sys
import getpass
import unicodedata
import copy

from os import stat
from pwd import getpwuid

import logging
from logger import build_logger
logger = build_logger("replace", level=logging.INFO)


# important constants:
ENCODING_INPUT_FILES = "utf8"

# colors
CRED = '\033[31m'
CBYELLOW = '\033[1;33m'
CBWHITE = '\033[1;37m'
CBPURPLE = '\033[1;35m'
BBLACK = '\033[1;30m'
CLIGHTBLUE = '\033[94m'
CBBLUE = '\033[1;34m'
CNORMAL_WHITE = '\033[0m'

COCCURRENCES = CBPURPLE
CFILE_PATHS = CBBLUE
CNORMAL_TEXT_IN_FILES = CBWHITE

# indicator strings
ASK_CONFIRMATION_INDICATORS_STRINGS = ["--ask_confirmation", "--ask"]
CASE_SENSITIVE_INDICATORS_STRINGS = ["--case_sensitive", "--case_respect"]
INITIAL_STRING_INDICATORS_STRINGS = ["--initial_string", "--initial", "--init"]
DESTINATION_STRING_INDICATORS_STRINGS = ["--destination_string", "--destination", "--dest"]
DIRECTORY_PATH_TO_APPLY_INDICATORS_STRINGS = ["--directory_path", "--dirpath", "--path"]
LIST_FILES_PATHS_TO_APPLY_INDICATORS_STRINGS = ["--file_paths_list", "--file_paths"]
FILENAME_MUST_END_BY_INDICATORS_STRINGS = ["--filename_must_end_by", "--end_by"]
NO_ASK_CONFIRMATION_INDICATORS_STRINGS = ["--no_ask_confirmation", "--no_ask"]
CASE_INSENSITIVE_INDICATORS_STRINGS = ["--case_insensitive", "--no_case_respect"]
BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS = ["--extension_filter", "--no_all_extensions"]
NO_BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS = ["--all_extensions", "--no_extension_filter"]
ADD_EXCLUDED_EXTENSIONS_INDICATORS_STRINGS = ["--add_excluded_extensions", "--filter_extensions"]
ADD_EXCLUDED_STRINGS_INDICATORS_STRINGS = ["--add_excluded_strings", "--filter_strings"]
EXCLUDED_PATHS_INDICATORS_STRINGS = ["--excluded_paths"]
NO_BINARY_INDICATORS_STRINGS = ["--binary_exclusion", "--no_binary"]
BINARY_INDICATORS_STRINGS = ["--binary_accepted", "--no_binary_exclusion", "--binary"]
NO_SYMLINK_INDICATORS_STRINGS = ["--symlink_exclusion", "--no_symlink"]
SYMLINK_INDICATORS_STRINGS = ["--symlink_accepted", "--no_symlink_exclusion", "--symlink"]
END_INDICATORS_STRINGS = ["end_last_param", "--end_param", "--end"]

# black list extensions
AUDIO_EXTENSIONS = ["mp3", "MP3", "wav", "WAV", "m4a", "M4A", "aac", "AAC", "mp1", "MP1", "mp2", "MP2", "mpg", "MPG", "flac", "FLAC"]
IMAGE_EXTENSIONS = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG", "tif", "TIF", "gif", "GIF", "bmp", "BMP", "pjpeg", "PJPEG"]
VIDEO_EXTENSIONS = ["mp4", "MP4", "mpeg", "MPEG", "avi", "AVI", "wma", "WMA", "ogg", "OGG", "quicktime", "QUICKTIME",
                    "webm", "WEBM", "mp2t", "MP2T", "flv", "FLV", "mov", "MOV", "webm", "WEBM", "mkv", "MKV"]
PROGRAMMING_EXTENSIONS = ["class", "CLASS"]

BLACK_LIST_EXTENSIONS_LIST = AUDIO_EXTENSIONS + IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + PROGRAMMING_EXTENSIONS


# supported short indicators
SUPPORTED_SHORT_INDICATORS = ['l', 'r', 's', 'a', 'c']


def check_help_request(arguments):
    if len(arguments) == 2 and (arguments[1] == "-h" or arguments[1] == "--help"):
        replace_script_path = get_full_path_joined(arguments[0])
        README_path = os.path.normpath(os.path.join(replace_script_path, "../../README.md"))

        f = open(README_path, 'r')
        print("\n\t#######      replace documentation      #######\n\n")

        for line in f:
            # line = line.replace('# ', '')
            line = line.replace('**', '')
            line = line.replace('*', '')
            print(" " + line)
        exit()


def check_nb_parameters(arguments):
    if len(arguments) < 3:
        logger.error("not enough arguments, needs at least the initial string and the destination string")
        logger.error("needs the replace mode (-l -r or -s), "
                     "the initial string, the destination string and the path to perform it")
        logger.error("a typical example would be: replace -l dog cat .")
        raise ValueError("not enough arguments")


def initiate_indicators_values():
    filename_must_end_by = []
    local = True  # default
    recursive = False
    specific = False
    ask_replace = True  # default
    case_sensitive = True  # default
    black_list_extensions = True  # default
    binary_accepted = False  # default
    symlink_accepted = False  # default
    excluded_strings = []
    excluded_extensions = []
    excluded_paths = []
    return filename_must_end_by, local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, \
           binary_accepted, symlink_accepted, excluded_strings, excluded_extensions, excluded_paths


def initiate_arguments_values():
    initial_string = None
    destination_string = None
    directory_path_to_apply = None
    list_files_paths_to_apply = []
    return initial_string, destination_string, directory_path_to_apply, list_files_paths_to_apply


def treat_input_parameters(input_parameters, filename_must_end_by, initial_string,
                           destination_string, directory_path_to_apply, list_files_paths_to_apply,
                           local, recursive, specific, ask_replace, case_sensitive, black_list_extensions,
                           binary_accepted, symlink_accepted, excluded_strings, excluded_extensions, excluded_paths):

    nb_args = len(input_parameters)
    not_compatible_shorts_indicators = []
    list_arguments_not_used_indexes = list(range(nb_args))
    list_arguments_not_used_indexes.pop(0)
    for arg_index, arg in enumerate(input_parameters[1:]):
        if arg.startswith("--"):
            if arg in FILENAME_MUST_END_BY_INDICATORS_STRINGS + INITIAL_STRING_INDICATORS_STRINGS + \
                    DESTINATION_STRING_INDICATORS_STRINGS + DIRECTORY_PATH_TO_APPLY_INDICATORS_STRINGS + \
                    LIST_FILES_PATHS_TO_APPLY_INDICATORS_STRINGS + ASK_CONFIRMATION_INDICATORS_STRINGS + \
                    NO_ASK_CONFIRMATION_INDICATORS_STRINGS + CASE_SENSITIVE_INDICATORS_STRINGS + \
                    CASE_INSENSITIVE_INDICATORS_STRINGS + NO_BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS + \
                    BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS + ADD_EXCLUDED_EXTENSIONS_INDICATORS_STRINGS + \
                    EXCLUDED_PATHS_INDICATORS_STRINGS + ADD_EXCLUDED_STRINGS_INDICATORS_STRINGS + \
                    BINARY_INDICATORS_STRINGS + NO_BINARY_INDICATORS_STRINGS + \
                    SYMLINK_INDICATORS_STRINGS + NO_SYMLINK_INDICATORS_STRINGS + END_INDICATORS_STRINGS:

                if arg in ASK_CONFIRMATION_INDICATORS_STRINGS:
                    ask_replace = True
                elif arg in NO_ASK_CONFIRMATION_INDICATORS_STRINGS:
                    ask_replace = False
                elif arg in CASE_SENSITIVE_INDICATORS_STRINGS:
                    case_sensitive = True
                elif arg in CASE_INSENSITIVE_INDICATORS_STRINGS:
                    case_sensitive = False
                elif arg in NO_BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS:
                    black_list_extensions = False
                elif arg in BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS:
                    black_list_extensions = True
                elif arg in BINARY_INDICATORS_STRINGS:
                    binary_accepted = True
                elif arg in NO_BINARY_INDICATORS_STRINGS:
                    binary_accepted = False
                elif arg in SYMLINK_INDICATORS_STRINGS:
                    symlink_accepted = True
                elif arg in NO_SYMLINK_INDICATORS_STRINGS:
                    symlink_accepted = False
                elif arg in END_INDICATORS_STRINGS:
                    pass

                elif arg_index < nb_args - 1:
                    if arg in FILENAME_MUST_END_BY_INDICATORS_STRINGS:
                        for potential_end_filter_index, potential_end_filter in enumerate(
                                input_parameters[arg_index + 2:]):
                            if not potential_end_filter.startswith("-"):
                                filename_must_end_by.append(potential_end_filter)
                                list_arguments_not_used_indexes.remove(arg_index + 2 + potential_end_filter_index)
                            else:
                                break
                    elif arg in EXCLUDED_PATHS_INDICATORS_STRINGS:
                        for potential_file_path_to_exclude_index, potential_file_path_to_exclude in enumerate(
                                input_parameters[arg_index + 2:]):
                            if not potential_file_path_to_exclude.startswith("-"):
                                potential_file_path_to_exclude = get_full_path_joined(potential_file_path_to_exclude)
                                list_arguments_not_used_indexes.remove(
                                    arg_index + 2 + potential_file_path_to_exclude_index)

                                if check_path_exists(potential_file_path_to_exclude):
                                    excluded_paths.append(potential_file_path_to_exclude)
                            else:
                                break

                    elif arg in ADD_EXCLUDED_EXTENSIONS_INDICATORS_STRINGS:
                        for potential_new_excluded_extension_index, potential_new_excluded_extension in enumerate(
                                input_parameters[arg_index + 2:]):
                            if not potential_new_excluded_extension.startswith("-"):
                                excluded_extensions.append(potential_new_excluded_extension)
                                list_arguments_not_used_indexes.remove(
                                    arg_index + 2 + potential_new_excluded_extension_index)

                            else:
                                break

                    elif arg in ADD_EXCLUDED_STRINGS_INDICATORS_STRINGS:
                        for potential_new_excluded_string_index, potential_new_excluded_string in enumerate(
                                input_parameters[arg_index + 2:]):
                            if not potential_new_excluded_string.startswith("-"):
                                excluded_strings.append(potential_new_excluded_string)
                                list_arguments_not_used_indexes.remove(
                                    arg_index + 2 + potential_new_excluded_string_index)

                            else:
                                break

                    elif arg in INITIAL_STRING_INDICATORS_STRINGS:
                        initial_string = input_parameters[arg_index + 2]
                        list_arguments_not_used_indexes.remove(arg_index + 2)
                    elif arg in DESTINATION_STRING_INDICATORS_STRINGS:
                        destination_string = input_parameters[arg_index + 2]
                        list_arguments_not_used_indexes.remove(arg_index + 2)
                    elif arg in DIRECTORY_PATH_TO_APPLY_INDICATORS_STRINGS:
                        directory_path_to_apply = input_parameters[arg_index + 2]
                        list_arguments_not_used_indexes.remove(arg_index + 2)
                    elif arg in LIST_FILES_PATHS_TO_APPLY_INDICATORS_STRINGS:
                        for potential_file_path_to_replace_index, potential_file_path_to_replace in enumerate(
                                input_parameters[arg_index + 2:]):
                            if not potential_file_path_to_replace.startswith("-"):
                                list_files_paths_to_apply.append(potential_file_path_to_replace)
                                list_arguments_not_used_indexes.remove(
                                    arg_index + 2 + potential_file_path_to_replace_index)
                            else:
                                break

                else:
                    logger.error("no parameter after %s indicator" % arg)
                    raise ValueError("needs a parameter after the %s indicator" % arg)

                list_arguments_not_used_indexes.remove(arg_index + 1)

            else:
                logger.error("the indicator %s is not supported" % arg)
                raise ValueError("please remove the %s parameter from the command" % arg)
        elif arg.startswith("-"):
            for short_indicator in arg[1:]:
                if short_indicator not in SUPPORTED_SHORT_INDICATORS:
                    logger.error("the short indicator -%s is not supported" % short_indicator)
                    raise ValueError("please remove the -%s short indicator from the command" % short_indicator)
                elif short_indicator in not_compatible_shorts_indicators:
                    logger.error("the short indicator -%s is not compatible with "
                                 "these short indicators %s" % (short_indicator, not_compatible_shorts_indicators))
                    raise ValueError("please remove one of the incompatibles shorts indicators from the command")
                elif short_indicator == 'l':
                    local = True
                    not_compatible_shorts_indicators += ['r', 's']
                elif short_indicator == 'r':
                    recursive = True
                    local = False
                    not_compatible_shorts_indicators += ['l', 's']
                elif short_indicator == 's':
                    specific = True
                    local = False
                    not_compatible_shorts_indicators += ['l', 'r']
                elif short_indicator == 'a':
                    ask_replace = True
                elif short_indicator == 'c':
                    case_sensitive = True

            list_arguments_not_used_indexes.remove(arg_index + 1)
    return filename_must_end_by, initial_string, destination_string, directory_path_to_apply, list_files_paths_to_apply, \
           local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, binary_accepted, \
           symlink_accepted, excluded_strings, excluded_extensions, excluded_paths, list_arguments_not_used_indexes


def check_only_one_replace_mode_picked(local, specific, recursive):
    nb_of_true = 0
    for replace_mode in [local, specific, recursive]:
        if replace_mode:
            nb_of_true += 1
    if nb_of_true != 1:
        logger.error("the replace mode can only be \"local\", \"recursive\" or \"specific\"")
        raise ValueError("please pick only one mode with the -l, -r or -s short options")


def get_final_pmts_local_recursive(directory_path_to_apply, destination_string, initial_string, local, recursive,
                                   input_params, list_arguments_not_used_indexes):
    if directory_path_to_apply is None:
        if not list_arguments_not_used_indexes:
            logger.error("arguments are missing ... please review the command syntax.")
            missing_arguments_local_recursive_error(local, recursive)

        directory_path_to_apply = input_params[list_arguments_not_used_indexes[-1]]
        list_arguments_not_used_indexes.pop()
    if destination_string is None:
        if not list_arguments_not_used_indexes:
            logger.error("arguments are missing ... please review the command syntax.")
            missing_arguments_local_recursive_error(local, recursive)

        destination_string = input_params[list_arguments_not_used_indexes[-1]]
        list_arguments_not_used_indexes.pop()
    if initial_string is None:
        if not list_arguments_not_used_indexes:
            logger.error("arguments are missing ... please review the command syntax.")
            missing_arguments_local_recursive_error(local, recursive)

        initial_string = input_params[list_arguments_not_used_indexes[-1]]
        list_arguments_not_used_indexes.pop()

    if directory_path_to_apply is None or destination_string is None or initial_string is None:
        logger.error("arguments are missing ... please review the command syntax.")
        missing_arguments_local_recursive_error(local, recursive)

    if list_arguments_not_used_indexes:
        logger.error("too much arguments entered ... please review the command syntax.")
        missing_arguments_local_recursive_error(local, recursive)

    return directory_path_to_apply, destination_string, initial_string


def missing_arguments_local_recursive_error(local, recursive):
    if local:
        raise ValueError("for a \"local replace\" please precise the \"initial string\", the \"destination string\" "
                         "and the \"directory path\" to apply the local replacement\na correct command would be: "
                         "replace -l titi toto /home/toto/documents/titi_folder")
    if recursive:
        raise ValueError("for a \"recursive replace\" please precise the \"initial string\", the \"destination string\" "
                         "and the \"directory path\" to apply the recursive replacement from\na "
                         "correct command would be: replace -r titi toto /home/toto/documents/titi_folder")


def get_final_pmts_specific(list_files_paths_to_apply, destination_string, initial_string,
                            specific, input_params, list_arguments_not_used_indexes):
    if initial_string is None:
        if not list_arguments_not_used_indexes:
            logger.error("arguments are missing ... please review the command syntax.")
            missing_arguments_specific_error(specific)

        initial_string = input_params[list_arguments_not_used_indexes[0]]
        list_arguments_not_used_indexes.pop(0)

    if destination_string is None:
        if not list_arguments_not_used_indexes:
            logger.error("arguments are missing ... please review the command syntax.")
            missing_arguments_specific_error(specific)

        destination_string = input_params[list_arguments_not_used_indexes[0]]
        list_arguments_not_used_indexes.pop(0)

    if not list_files_paths_to_apply:
        if not list_arguments_not_used_indexes:
            logger.error("arguments are missing ... please review the command syntax.")
            missing_arguments_specific_error(specific)
        for parameter_not_already_used_index in list_arguments_not_used_indexes:
            list_files_paths_to_apply.append(input_params[parameter_not_already_used_index])
        list_arguments_not_used_indexes = []

    if list_arguments_not_used_indexes:
        logger.error("too much arguments entered ... please review the command syntax.")
        missing_arguments_specific_error(specific)

    return list_files_paths_to_apply, destination_string, initial_string


def missing_arguments_specific_error(specific):
    if specific:
        raise ValueError("for a \"specific replace\" please precise the \"initial string\", "
                         "the \"destination string\" and the \"list files paths\" to apply "
                         "the specific replacement\na correct command would be: "
                         "replace -s titi toto /home/toto/documents/test00 "
                         "documents/titi_folder/test01 documents/titi_folder/secret_titi_folder/test02")


def check_initial_string_in_file(file_path, initial_string, case_sensitive):

    try:
        if case_sensitive:
            for line in open(file_path, 'r', encoding=ENCODING_INPUT_FILES):
                if initial_string in line:
                    return True
            return False
        elif not case_sensitive:
            for line in open(file_path, 'r', encoding=ENCODING_INPUT_FILES):
                if caseless_str1_in_str2(initial_string, line):
                    return True
            return False

    except PermissionError:
        print("\tyou don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE)
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False
    except UnicodeDecodeError:
        print("\tthe file " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE + " owns non unicode characters")
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False
    except:
        raise ValueError("the file %s seems to cause problem to be opened" % file_path)


def get_string_positions_in_lines(string, line, case_sensitive):
    start_string_indexes = []
    if case_sensitive:
        for index in range(len(line)):
            if line[index:].startswith(string):
                start_string_indexes.append(index)
    if not case_sensitive:
        for index in range(len(line)):
            if normalize_caseless(line)[index:].startswith(normalize_caseless(string)):
                start_string_indexes.append(index)
    return start_string_indexes


def print_WARNING_in_red():
    print(CRED + "\n\tWARNING:" + CNORMAL_WHITE, end='')


def check_user_permissions(file_path):
    current_user = getpass.getuser()
    owner_file = getpwuid(stat(file_path).st_uid).pw_name
    if owner_file != current_user:
        print_WARNING_in_red()
        print(" the file " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE + " is owned by " + CFILE_PATHS +
              "%s" % owner_file + CNORMAL_WHITE + ", might be necessary to manage its permissions\n")


def print_previous_lines(previous_lines, line_nb):
    if len(previous_lines) == 2:
        print(CBYELLOW + "\t    %s: " % (line_nb - 2) + CNORMAL_TEXT_IN_FILES + "%s" % previous_lines[1], end='')
        print(CBYELLOW + "\t    %s: " % (line_nb - 1) + CNORMAL_TEXT_IN_FILES + "%s" % previous_lines[0] + CNORMAL_WHITE, end='')
    elif len(previous_lines) == 1:
        print(CBYELLOW + "\t    %s: " % (line_nb - 1) + CNORMAL_TEXT_IN_FILES + "%s" % previous_lines[0] + CNORMAL_WHITE, end='')


def displaying_line_highlighting_initial_strings(line, line_nb, start_string_positions, initial_string, previous_lines):
    if len(start_string_positions) > 1:
        print("\n\tthere are several occurrences of " + COCCURRENCES + "\"%s\"" % initial_string +
              CNORMAL_WHITE + " in this line:\n")

    print_previous_lines(previous_lines, line_nb)

    print(COCCURRENCES + "\t    %s: " % line_nb + CNORMAL_TEXT_IN_FILES + "%s" % line[0:start_string_positions[0]],
          end='')
    for string_list_index, string_index in enumerate(start_string_positions):
        print(COCCURRENCES + "%s" % initial_string + CNORMAL_WHITE, end='')
        if string_list_index == len(start_string_positions) - 1:
            print(CNORMAL_TEXT_IN_FILES + "%s" % line[string_index + len(initial_string):] + CNORMAL_WHITE, end='')
        else:
            print(CNORMAL_TEXT_IN_FILES + "%s" % line[string_index + len(initial_string):start_string_positions[
                string_list_index + 1]] + CNORMAL_WHITE, end='')
    return start_string_positions


def displaying_line_highlighting_defined_initial_string(new_line, line, initial_string,
                                                        defined_initial_string_start_position):
    print(CNORMAL_TEXT_IN_FILES + "\t\t%s" % new_line, end='')
    print(COCCURRENCES + "%s" % initial_string + CNORMAL_WHITE, end='')
    print(CNORMAL_TEXT_IN_FILES + "%s" %
          line[defined_initial_string_start_position + len(initial_string):] + CNORMAL_WHITE, end='')


def normalize_caseless(string):
    return unicodedata.normalize("NFKD", string.casefold())


def caseless_equal(str1, str2):
    return normalize_caseless(str1) == normalize_caseless(str2)


def caseless_str1_in_str2(str1, str2):
    if normalize_caseless(str1) in normalize_caseless(str2):
        return True
    else:
        return False


def abort_process(current_file, temporary_file_path):
    current_file.close()
    os.remove(temporary_file_path)
    print(CBYELLOW + "\n\n\t\t\taborted ...\n\t\t\t\tSee you later\n" + CNORMAL_WHITE)
    exit()


def complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                      start_string_positions, len_initial_string):
    if start_string_index == nb_occurrences_in_line - 1:
        new_line += line[start_string_position + len_initial_string:]
    else:
        new_line += line[start_string_position + len_initial_string:start_string_positions[start_string_index + 1]]
    return new_line


def build_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                   start_string_positions, initial_string):
    new_line += initial_string
    new_line = complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                 start_string_position,
                                 start_string_positions, len(initial_string))
    return new_line


def multi_replacement_on_same_line(line, start_string_positions, initial_string, destination_string,
                                   nb_occurrences_replaced, current_file, temporary_file_path, skip_file):
    new_line = line[:start_string_positions[0]]
    nb_occurrences_in_line = len(start_string_positions)

    for start_string_index, start_string_position in enumerate(start_string_positions):

        if skip_file:
            new_line = build_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                                      start_string_positions, initial_string)
        else:
            print(CBYELLOW + "\n\toccurrence %s:" % (start_string_index+1) + CNORMAL_WHITE)
            displaying_line_highlighting_defined_initial_string(new_line, line, initial_string, start_string_position)
            replace_confirmation = input("\n\tperform replacement for this occurrence?\n\t\t[Enter] to "
                                         "proceed\t\t[fF] to skip the rest of the file\n\t\t[oO] to "
                                         "skip this occurrence\t[aA] to abort the replace process\n\t")
            if replace_confirmation == "":

                print(CFILE_PATHS + "\t\t\tdone\n\n" + CNORMAL_WHITE)
                new_line += destination_string
                new_line = complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                             start_string_position,
                                             start_string_positions, len(initial_string))

                nb_occurrences_replaced += 1
            elif replace_confirmation in ["a", "A"]:
                abort_process(current_file, temporary_file_path)
            else:
                new_line = build_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                          start_string_position, start_string_positions, initial_string)
                print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)

            if replace_confirmation in ["f", "F"]:
                skip_file = True

    current_file.write(new_line)
    return nb_occurrences_replaced, skip_file


def replace_one_occurrence_asked(replace_confirmation, current_file, temporary_file_path, initial_string,
                                 destination_string, line, nb_occurrences_replaced, case_sensitive, skip_file):
    if replace_confirmation == "":
        if case_sensitive:
            current_file.write(re.sub(initial_string, destination_string, line))
        else:
            current_file.write(re.sub(initial_string, destination_string, line, flags=re.I))
        nb_occurrences_replaced += 1
        print(CFILE_PATHS + "\t\t\tdone\n\n" + CNORMAL_WHITE)
    elif replace_confirmation in ["a", "A"]:
        abort_process(current_file, temporary_file_path)
    else:
        current_file.write(line)
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
    if replace_confirmation in ["f", "F"]:
        skip_file = True
    return nb_occurrences_replaced, skip_file


def update_previous_lines(previous_lines, line):
    if len(previous_lines) == 0:
        previous_lines.append(copy.deepcopy(line))

    elif len(previous_lines) == 1:
        previous_lines.append(copy.deepcopy(previous_lines[0]))
    elif len(previous_lines) == 2:
        previous_lines[1] = copy.deepcopy(previous_lines[0])
        previous_lines[0] = copy.deepcopy(line)
    else:
        logger.error("previous lines can not have more than 2 lines, check %s" % previous_lines)
        raise ValueError("check previous lines: %s" % previous_lines)


def find_a_temporary_file_not_existing(file_path):
    for i in range(9):
        temporary_file_path = file_path + ".rp0" + str(i+1) + ".tmp"
        if not os.path.exists(temporary_file_path):
            return temporary_file_path
    raise ValueError("all the available tmp extensions are used for the %s path" % file_path)


def file_replace(file_path, temporary_file_path, initial_string, destination_string, nb_occurrences_found,
                 nb_occurrences_replaced, ask_replace, case_sensitive, file_mask):

    current_file = open(temporary_file_path, "w")
    if not os.path.isfile(file_path):
        logger.error("the file %s doesn't exist" % file_path)
        return nb_occurrences_replaced

    print("\nthere is " + COCCURRENCES + "\"%s\"" % initial_string + CNORMAL_WHITE +
          " in the file " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE)
    print("\treplacing " + COCCURRENCES + "\"%s\"" % initial_string + CNORMAL_WHITE +
          " by " + COCCURRENCES + "\"%s\"" % destination_string + CNORMAL_WHITE +
          " in " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE + " for the following lines:")

    previous_lines = []
    skip_file = False

    for line_index, line in enumerate(open(file_path, encoding=ENCODING_INPUT_FILES)):
        line_nb = line_index + 1
        if case_sensitive:
            if initial_string in line and not skip_file:
                start_string_positions = get_string_positions_in_lines(initial_string, line, case_sensitive)
                displaying_line_highlighting_initial_strings(line, line_nb, start_string_positions, initial_string,
                                                             previous_lines)
                nb_occurrences_found += len(start_string_positions)
                if not ask_replace:
                    nb_occurrences_replaced += len(start_string_positions)
                    current_file.write(re.sub(initial_string, destination_string, line))
                elif ask_replace:
                    if len(start_string_positions) == 1:
                        replace_confirmation = input("\n\tperform replacement?\n\t\t[Enter] to proceed\t\t[fF] to "
                                                     "skip the rest of the file\n\t\t[oO] to skip "
                                                     "this occurrence\t[aA] to abort the replace process\n\t")

                        nb_occurrences_replaced, skip_file = replace_one_occurrence_asked(replace_confirmation,
                                                                                          current_file,
                                                                                          temporary_file_path,
                                                                                          initial_string,
                                                                                          destination_string, line,
                                                                                          nb_occurrences_replaced,
                                                                                          case_sensitive, skip_file)
                    else:
                        nb_occurrences_replaced, skip_file = multi_replacement_on_same_line(line,
                                                                                            start_string_positions,
                                                                                            initial_string,
                                                                                            destination_string,
                                                                                            nb_occurrences_replaced,
                                                                                            current_file,
                                                                                            temporary_file_path,
                                                                                            skip_file)

                else:
                    logger.error("the ask_replace parameter can only be \"True\" or \"False\"")
                    raise ValueError("the ask_replace parameter can not be %s" % ask_replace)
            else:
                current_file.write(line)

        elif not case_sensitive:
            if caseless_str1_in_str2(initial_string, line) and not skip_file:
                start_string_positions = get_string_positions_in_lines(initial_string, line, case_sensitive)
                displaying_line_highlighting_initial_strings(line, line_nb, start_string_positions,
                                                             initial_string, previous_lines)
                nb_occurrences_found += len(start_string_positions)
                if not ask_replace:
                    nb_occurrences_replaced += len(start_string_positions)
                    current_file.write(re.sub(initial_string, destination_string, line, flags=re.I))
                elif ask_replace:

                    if len(start_string_positions) == 1:
                        replace_confirmation = input("\n\tperform replacement?\n\t\t[Enter] to proceed\t\t[fF] to "
                                                     "skip the rest of the file\n\t\t[oO] to skip "
                                                     "this occurrence\t[aA] to abort the replace process\n\t")

                        nb_occurrences_replaced, skip_file = replace_one_occurrence_asked(replace_confirmation,
                                                                                          current_file,
                                                                                          temporary_file_path,
                                                                                          initial_string,
                                                                                          destination_string, line,
                                                                                          nb_occurrences_replaced,
                                                                                          case_sensitive, skip_file)

                    else:
                        nb_occurrences_replaced, skip_file = multi_replacement_on_same_line(line,
                                                                                            start_string_positions,
                                                                                            initial_string,
                                                                                            destination_string,
                                                                                            nb_occurrences_replaced,
                                                                                            current_file,
                                                                                            temporary_file_path,
                                                                                            skip_file)
                else:
                    logger.error("the ask_replace parameter can only be \"True\" or \"False\"")
                    raise ValueError("the ask_replace parameter can not be %s" % ask_replace)
            else:
                current_file.write(line)

        else:
            logger.error("the case_sensitive parameter can only be \"True\" or \"False\"")
            raise ValueError("the case_sensitive parameter can not be %s" % case_sensitive)

        update_previous_lines(previous_lines, line)

    current_file.close()
    os.remove(file_path)
    os.rename(temporary_file_path, file_path)
    os.chmod(file_path, int(file_mask, 8))

    return nb_occurrences_found, nb_occurrences_replaced


def check_file_extension_in_blacklist(file_path):
    for black_list_extension in BLACK_LIST_EXTENSIONS_LIST:
        if file_path.endswith(black_list_extension):
            print_WARNING_in_red()
            print("the file %s owns the extension %s that is not accepted by default" % (file_path, black_list_extension))
            print("\tuse one of these parameters %s if you want to perform replacement "
                  "in this kind of file anyway" % NO_BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS)
            print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
            return True
    return False


def check_filename_must_end_by(filename_must_end_by, file_path):
    for acceptable_filename_end in filename_must_end_by:
        if file_path.endswith(acceptable_filename_end):
            return True
    print_WARNING_in_red()
    print("the file %s doesn't end by the acceptable end extensions you entered: %s" % (file_path, filename_must_end_by))
    print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
    return False


def check_file_owns_excluded_path(excluded_paths, file_path):
    for excluded_path in excluded_paths:
        if file_path.startswith(excluded_path):
            print_WARNING_in_red()
            print("the file %s is excluded regarding the excluded path %s you entered" % (file_path, excluded_path))
            print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
            return True
    return False


def check_file_owns_excluded_extension(excluded_extensions, file_path):
    for excluded_extension in excluded_extensions:
        if file_path.endswith(excluded_extension):
            print_WARNING_in_red()
            print("the file %s is excluded regarding the excluded extension %s you entered" % (file_path, excluded_extension))
            print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
            return True
    return False


def check_file_owns_excluded_string(excluded_strings, file_path):
    for excluded_string in excluded_strings:
        if excluded_string in file_path:
            print_WARNING_in_red()
            print("the file %s is excluded regarding the excluded string %s you entered" % (file_path, excluded_string))
            print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
            return True
    return False


def check_able_open_file(file_path):

    try:
        open_test = open(file_path, 'r', encoding=ENCODING_INPUT_FILES)
        open_test.close()
        return True
    except FileNotFoundError:
        print("\tthe file " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE + " doesn't exist")
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False
    except PermissionError:
        print("\tyou don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE)
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False
    except IsADirectoryError:
        print("\t the path " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE + "is a directory, not a file")
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False
    except OSError:
        print("\t no such device or address " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE)
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False


def check_able_create_temporary(temporary_file_path, file_mask):

    try:
        open_test = open(temporary_file_path, 'w+')
        open_test.close()
        os.chmod(temporary_file_path, int(file_mask, 8))
        os.remove(temporary_file_path)
        return True
    except FileNotFoundError:
        print("\tthe file " + CFILE_PATHS + "%s" % temporary_file_path + CNORMAL_WHITE + " doesn't exist")
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False
    except PermissionError:
        print("\tyou don't have the permission to create the file " + CFILE_PATHS + "%s" % temporary_file_path + CNORMAL_WHITE)
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False
    except IsADirectoryError:
        print("\t the path " + CFILE_PATHS + "%s" % temporary_file_path + CNORMAL_WHITE + "is a directory, not a file")
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return False


def check_binary_file(file_path):
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    try:
        if is_binary_string(open(file_path, 'rb').read(1024)):
            print_WARNING_in_red()
            print("the file %s is a binary file" % file_path)
            print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
            return True
        return False
    except PermissionError:
        print("\tyou don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CNORMAL_WHITE)
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return True


def check_symlink_path(file_path):
    if os.path.islink(file_path):
        print_WARNING_in_red()
        print("the file %s is a symlink file" % file_path)
        print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
        return True
    return False


def get_temporary_file_path(file_path):
    temporary_file_path = file_path + ".tmp"
    if os.path.exists(temporary_file_path):
        temporary_file_path = find_a_temporary_file_not_existing(file_path)
    excluded_paths.append(temporary_file_path)
    return temporary_file_path


def get_file_permission_mask(file_path):
    # return oct(os.stat(file_path).st_mode & 0o777)[-3:]
    return oct(os.stat(file_path).st_mode & 0o777)


def replace_local_recursive(directory_path, initial_string, destination_string, black_list_extensions,
                            filename_must_end_by, excluded_paths, excluded_strings, excluded_extensions, local,
                            nb_occurrences_found, nb_occurrences_replaced, ask_replace, case_sensitive, binary_accepted,
                            symlink_accepted):
    for directory_path, directory_names, filenames in os.walk(directory_path):
        for filename in filenames:

            file_path = os.path.join(directory_path, filename)

            if check_file_owns_excluded_path(excluded_paths, file_path):
                continue

            if check_file_owns_excluded_extension(excluded_extensions, file_path):
                continue

            if check_file_owns_excluded_string(excluded_strings, file_path):
                continue

            if not check_path_exists(file_path):
                print("\t\tthe file path %s seems to cause problem, might be a broken simlink" % file_path)
                print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
                continue

            check_user_permissions(file_path)
            if not check_able_open_file(file_path):
                continue

            if black_list_extensions:
                if check_file_extension_in_blacklist(file_path):
                    continue

            if not symlink_accepted:
                if check_symlink_path(file_path):
                    continue

            if not binary_accepted:
                if check_binary_file(file_path):
                    continue

            if filename_must_end_by:
                if not check_filename_must_end_by(filename_must_end_by, file_path):
                    continue

            file_mask = get_file_permission_mask(file_path)

            temporary_file_path = get_temporary_file_path(file_path)
            if not check_able_create_temporary(temporary_file_path, file_mask):
                continue

            if check_initial_string_in_file(file_path, initial_string, case_sensitive):
                nb_occurrences_found, nb_occurrences_replaced = file_replace(file_path, temporary_file_path,
                                                                             initial_string, destination_string,
                                                                             nb_occurrences_found,
                                                                             nb_occurrences_replaced,
                                                                             ask_replace, case_sensitive, file_mask)
        if local:
            break
    return nb_occurrences_found, nb_occurrences_replaced


def check_path_folder_exists(folder_path):
    if not os.path.isdir(folder_path):
        print_WARNING_in_red()
        print("the %s folder path doesn't exist" % folder_path)
        raise ValueError("the directory path to apply %s doesn't exist, you may review it" % directory_path_to_apply)


def check_path_exists(file_path):
    if not os.path.exists(file_path):
        print_WARNING_in_red()
        print("the %s path doesn't exist" % file_path)
        return False
    return True


def replace_specific(list_files_paths_to_apply, initial_string, destination_string,
                     nb_occurrences_found, nb_occurrences_replaced, black_list_extensions, ask_replace, case_sensitive,
                     binary_accepted, symlink_accepted):
    for file_path in list_files_paths_to_apply:

        if not check_path_exists(file_path):
            print("\t\tthe file path %s seems to cause problem, might be a broken simlink" % file_path)
            print(CFILE_PATHS + "\n\t\t\tskipped\n\n" + CNORMAL_WHITE)
            continue

        check_user_permissions(file_path)
        if not check_able_open_file(file_path):
            continue

        if black_list_extensions:
            if check_file_extension_in_blacklist(file_path):
                continue

        if not symlink_accepted:
            if check_symlink_path(file_path):
                continue

        if not binary_accepted:
            if check_binary_file(file_path):
                continue

        file_mask = get_file_permission_mask(file_path)
        temporary_file_path = get_temporary_file_path(file_path)
        if not check_able_create_temporary(temporary_file_path, file_mask):
            continue

        if check_initial_string_in_file(file_path, initial_string, case_sensitive):
            nb_occurrences_found, nb_occurrences_replaced = file_replace(file_path, temporary_file_path, initial_string,
                                                   destination_string, nb_occurrences_found,
                                                   nb_occurrences_replaced, ask_replace, case_sensitive, file_mask)
    return nb_occurrences_found, nb_occurrences_replaced


def display_occurrences_found_message(nb_occurrences_found, nb_occurrences_replaced, initial_string):
    if nb_occurrences_found == 0:
        print(CFILE_PATHS + "\n\t%s" % nb_occurrences_found + CNORMAL_WHITE + " occurrence of " + COCCURRENCES +
              "%s" % initial_string + CNORMAL_WHITE + " found")
    else:
        print(CFILE_PATHS + "\n\t%s" % nb_occurrences_found + CNORMAL_WHITE + " occurrences of " + COCCURRENCES +
              "%s" % initial_string + CNORMAL_WHITE + " found and " + CFILE_PATHS + "%s" % nb_occurrences_replaced +
              CNORMAL_WHITE + " replaced")


def get_full_paths(directory_path_to_apply, list_files_paths_to_apply):
    if list_files_paths_to_apply:
        filepaths_list = []

        for filename in list_files_paths_to_apply:
            filepaths_list.append(get_full_path_joined(filename))

        list_files_paths_to_apply = filepaths_list

    if directory_path_to_apply is not None:
        directory_path_to_apply = get_full_path_joined(directory_path_to_apply)

    return directory_path_to_apply, list_files_paths_to_apply


def get_full_path_joined(given_path):
    return os.path.normpath((os.path.join(os.getcwd(), os.path.expanduser(given_path))))


def check_integrity_of_mode_request(local, recursive, specific, directory_path_to_apply, list_files_paths_to_apply):
    if local or recursive:
        if list_files_paths_to_apply:
            print_WARNING_in_red()
            print("the replace mode is not specific, list_files_paths_to_apply "
                  "should be empty and is: %s" % list_files_paths_to_apply)
            raise ValueError("list_files_paths_to_apply should be empty")
        if directory_path_to_apply is None:
            print_WARNING_in_red()
            print("the replace mode is not specific, directory_path_to_apply should not be None")
            raise ValueError("directory_path_to_apply should be defined")
        if not check_path_exists(directory_path_to_apply):
            raise ValueError("the directory path %s doesn't exist" % directory_path_to_apply)
        if not os.path.isdir(directory_path_to_apply):
            print("\n\t%s is a file, proceeding specific replace mode\n" % directory_path_to_apply)
            local = False
            recursive = False
            specific = True
            list_files_paths_to_apply.append(directory_path_to_apply)

    elif specific:
        if not list_files_paths_to_apply:
            print_WARNING_in_red()
            print("the replace mode is specific, list_files_paths_to_apply should not be empty and is: %s")
            raise ValueError("list_files_paths_to_apply should not be empty in specific mode replacement")
        if directory_path_to_apply is not None:
            print_WARNING_in_red()
            print("the replace mode is specific, directory_path_to_apply should be None")
            raise ValueError("directory_path_to_apply should not be defined")

        file_paths = []
        for filepath in list_files_paths_to_apply:
            if not check_path_exists(filepath):
                print("removing %s from the file list" % filepath)
            elif os.path.isdir(filepath):
                print("%s is a folder, removing it from the file list" % filepath)
            else:
                file_paths.append(filepath)

        list_files_paths_to_apply = file_paths

    return local, recursive, specific, directory_path_to_apply, list_files_paths_to_apply


if __name__ == '__main__':
    check_help_request(sys.argv)
    check_nb_parameters(sys.argv)
    filename_must_end_by, local, recursive, specific, ask_replace, case_sensitive, \
        black_list_extensions, binary_accepted, symlink_accepted, excluded_strings, \
        excluded_extensions, excluded_paths = initiate_indicators_values()

    initial_string, destination_string, directory_path_to_apply, list_files_paths_to_apply = initiate_arguments_values()

    filename_must_end_by, initial_string, destination_string, directory_path_to_apply, list_files_paths_to_apply, \
        local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, binary_accepted, \
        symlink_accepted, excluded_strings, excluded_extensions, excluded_paths, list_arguments_not_used_indexes = \
        treat_input_parameters(sys.argv, filename_must_end_by, initial_string, destination_string,
                               directory_path_to_apply, list_files_paths_to_apply, local, recursive, specific,
                               ask_replace, case_sensitive, black_list_extensions, binary_accepted, symlink_accepted,
                               excluded_strings, excluded_extensions, excluded_paths)

    check_only_one_replace_mode_picked(local, specific, recursive)

    # finalize getting all the parameters
    if local or recursive:
        directory_path_to_apply, destination_string, initial_string = \
            get_final_pmts_local_recursive(directory_path_to_apply, destination_string,
                                                              initial_string, local, recursive, sys.argv,
                                                              list_arguments_not_used_indexes)

    elif specific:
        list_files_paths_to_apply, destination_string, initial_string = \
            get_final_pmts_specific(list_files_paths_to_apply, destination_string,
                                                       initial_string, specific, sys.argv,
                                                       list_arguments_not_used_indexes)
    else:
        logger.error("the replace mode can only be \"local\", \"recursive\" or \"specific\"")
        raise ValueError("please pick only one mode with the -l, -r or -s short options")

    directory_path_to_apply, list_files_paths_to_apply = get_full_paths(directory_path_to_apply,
                                                                        list_files_paths_to_apply)
    local, recursive, specific, directory_path_to_apply, list_files_paths_to_apply = check_integrity_of_mode_request(
        local, recursive, specific, directory_path_to_apply, list_files_paths_to_apply)

    nb_occurrences_found = 0
    nb_occurrences_replaced = 0

    # apply the replace
    if local:
        nb_occurrences_found, nb_occurrences_replaced = \
            replace_local_recursive(directory_path_to_apply, initial_string, destination_string, black_list_extensions,
                                    filename_must_end_by, excluded_paths, excluded_strings, excluded_extensions, local,
                                    nb_occurrences_found, nb_occurrences_replaced, ask_replace, case_sensitive,
                                    binary_accepted, symlink_accepted)

    elif recursive:
        nb_occurrences_found, nb_occurrences_replaced = \
            replace_local_recursive(directory_path_to_apply, initial_string, destination_string, black_list_extensions,
                                    filename_must_end_by, excluded_paths, excluded_strings, excluded_extensions, local,
                                    nb_occurrences_found, nb_occurrences_replaced, ask_replace, case_sensitive,
                                    binary_accepted, symlink_accepted)

    elif specific:
        nb_occurrences_found, nb_occurrences_replaced = \
            replace_specific(list_files_paths_to_apply, initial_string, destination_string,
                             nb_occurrences_found, nb_occurrences_replaced, black_list_extensions, ask_replace,
                             case_sensitive, binary_accepted, symlink_accepted)
    else:
        logger.error("the replace mode can only be \"local\", \"recursive\" or \"specific\"")
        raise ValueError("please pick only one mode with the -l, -r or -s short options")

    display_occurrences_found_message(nb_occurrences_found, nb_occurrences_replaced, initial_string)
