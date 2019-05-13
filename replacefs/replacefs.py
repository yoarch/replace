#!/usr/bin/python

import os
import re
import sys
import getpass
import unicodedata
import copy

from os import stat
from pwd import getpwuid


# important constants:
ENCODING_INPUT_FILES = "utf8"

# colors
CBRED = '\033[38;5;196;1m'
CBORANGE = '\033[38;5;202;1m'
CBGREEN = '\033[38;5;40;1m'
CBYELLOW = '\033[1;33m'
CBWHITE = '\033[1;37m'
CBPURPLE = '\033[1;35m'
CBBLUE = '\033[1;34m'
CBASE = '\033[0m'

COCCURRENCES = CBPURPLE
CFILE_PATHS = CBBLUE
CTEXT_FILES = CBWHITE

# indicator strings
ASK_CONFIRMATION_INDICATORS_STRINGS = ["--ask_confirmation", "--ask"]
CASE_SENSITIVE_INDICATORS_STRINGS = ["--case_sensitive", "--case_respect"]
INITIAL_STRING_INDICATORS_STRINGS = ["--init_str", "--initial", "--init"]
DESTINATION_STRING_INDICATORS_STRINGS = ["--dest_str", "--destination", "--dest"]
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
    if len(arguments) == 1 and (arguments[0] == "-h" or arguments[0] == "--help"):
        README_path = "/usr/lib/replace/README.md"

        f = open(README_path, 'r')
        print(CFILE_PATHS + "\n\t#######      replace documentation      #######\n" + CBWHITE)

        for line in f:
            if line == "```sh\n" or line == "```\n" or line == "<pre>\n" or line == "</pre>\n":
                continue

            line = line.replace('```sh', '').replace('```', '').replace('<pre>', '').replace('</b>', '').\
                replace('<b>', '').replace('<!-- -->', '').replace('<br/>', '').replace('```sh', '').\
                replace('***', '').replace('***', '').replace('**', '').replace('*', '')

            print(" " + line, end='')
        print(CBASE)
        exit()


def check_nb_parameters(args):
    if len(args) < 2:
        ERROR("not enough arguments, needs at least the initial string and the destination string")
        ERROR("needs the replace mode (-l -r or -s), "
                     "the initial string, the destination string and the path to perform it")
        ERROR("a typical example would be: replace -l dog cat .")
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


def initiate_args_values():
    init_str = None
    dest_str = None
    dir_path_to_apply = None
    file_paths_to_apply = []
    nb_occs_found = 0
    nb_occs_replaced = 0
    return init_str, dest_str, dir_path_to_apply, file_paths_to_apply, nb_occs_found, nb_occs_replaced


def treat_input_parms(input_parms, filename_must_end_by, init_str,
                           dest_str, dir_path_to_apply, file_paths_to_apply,
                           local, recursive, specific, ask_replace, case_sensitive, black_list_extensions,
                           binary_accepted, symlink_accepted, excluded_strings, excluded_extensions, excluded_paths):

    nb_args = len(input_parms)
    not_compatible_shorts_indicators = []
    args_not_used_indexes = list(range(nb_args))
    for arg_index, arg in enumerate(input_parms):
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
                                input_parms[arg_index + 1:]):
                            if not potential_end_filter.startswith("-"):
                                filename_must_end_by.append(potential_end_filter)
                                args_not_used_indexes.remove(arg_index + 1 + potential_end_filter_index)
                            else:
                                break
                    elif arg in EXCLUDED_PATHS_INDICATORS_STRINGS:
                        for potential_file_path_to_exclude_index, potential_file_path_to_exclude in enumerate(
                                input_parms[arg_index + 1:]):
                            if not potential_file_path_to_exclude.startswith("-"):
                                potential_file_path_to_exclude = get_full_path_joined(potential_file_path_to_exclude)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_file_path_to_exclude_index)

                                if check_path_exists(potential_file_path_to_exclude):
                                    excluded_paths.append(potential_file_path_to_exclude)
                            else:
                                break

                    elif arg in ADD_EXCLUDED_EXTENSIONS_INDICATORS_STRINGS:
                        for potential_new_excluded_extension_index, potential_new_excluded_extension in enumerate(
                                input_parms[arg_index + 1:]):
                            if not potential_new_excluded_extension.startswith("-"):
                                excluded_extensions.append(potential_new_excluded_extension)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_new_excluded_extension_index)

                            else:
                                break

                    elif arg in ADD_EXCLUDED_STRINGS_INDICATORS_STRINGS:
                        for potential_new_excluded_string_index, potential_new_excluded_string in enumerate(
                                input_parms[arg_index + 1:]):
                            if not potential_new_excluded_string.startswith("-"):
                                excluded_strings.append(potential_new_excluded_string)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_new_excluded_string_index)

                            else:
                                break

                    elif arg in INITIAL_STRING_INDICATORS_STRINGS:
                        init_str = input_parms[arg_index + 1]
                        args_not_used_indexes.remove(arg_index + 1)
                    elif arg in DESTINATION_STRING_INDICATORS_STRINGS:
                        dest_str = input_parms[arg_index + 1]
                        args_not_used_indexes.remove(arg_index + 1)
                    elif arg in DIRECTORY_PATH_TO_APPLY_INDICATORS_STRINGS:
                        dir_path_to_apply = input_parms[arg_index + 1]
                        args_not_used_indexes.remove(arg_index + 1)
                    elif arg in LIST_FILES_PATHS_TO_APPLY_INDICATORS_STRINGS:
                        for potential_file_path_to_replace_index, potential_file_path_to_replace in enumerate(
                                input_parms[arg_index + 1:]):
                            if not potential_file_path_to_replace.startswith("-"):
                                file_paths_to_apply.append(potential_file_path_to_replace)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_file_path_to_replace_index)
                            else:
                                break

                else:
                    ERROR("no parameter after %s indicator" % arg)
                    raise ValueError("needs a parameter after the %s indicator" % arg)

                args_not_used_indexes.remove(arg_index)

            else:
                ERROR("the indicator %s is not supported" % arg)
                raise ValueError("please remove the %s parameter from the command" % arg)
        elif arg.startswith("-"):
            for short_indicator in arg[1:]:
                if short_indicator not in SUPPORTED_SHORT_INDICATORS:
                    ERROR("the short indicator -%s is not supported" % short_indicator)
                    raise ValueError("please remove the -%s short indicator from the command" % short_indicator)
                elif short_indicator in not_compatible_shorts_indicators:
                    ERROR("the short indicator -%s is not compatible with "
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

            args_not_used_indexes.remove(arg_index)
    return filename_must_end_by, init_str, dest_str, dir_path_to_apply, file_paths_to_apply, \
           local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, binary_accepted, \
           symlink_accepted, excluded_strings, excluded_extensions, excluded_paths, args_not_used_indexes


def check_only_one_replace_mode_picked(local, specific, recursive):
    nb_of_true = 0
    for replace_mode in [local, specific, recursive]:
        if replace_mode:
            nb_of_true += 1
    if nb_of_true != 1:
        ERROR("the replace mode can only be \"local\", \"recursive\" or \"specific\"")
        raise ValueError("please pick only one mode with the -l, -r or -s short options")


def get_final_parms_local_recursive(dir_path_to_apply, dest_str, init_str, local, recursive,
                                   input_parms, args_not_used_indexes):
    if dir_path_to_apply is None:
        if not args_not_used_indexes:
            ERROR("arguments are missing ... please review the command syntax.")
            missing_args_local_recursive_error(local, recursive)

        dir_path_to_apply = input_parms[args_not_used_indexes[-1]]
        args_not_used_indexes.pop()
    if dest_str is None:
        if not args_not_used_indexes:
            ERROR("arguments are missing ... please review the command syntax.")
            missing_args_local_recursive_error(local, recursive)

        dest_str = input_parms[args_not_used_indexes[-1]]
        args_not_used_indexes.pop()
    if init_str is None:
        if not args_not_used_indexes:
            ERROR("arguments are missing ... please review the command syntax.")
            missing_args_local_recursive_error(local, recursive)

        init_str = input_parms[args_not_used_indexes[-1]]
        args_not_used_indexes.pop()

    if dir_path_to_apply is None or dest_str is None or init_str is None:
        ERROR("arguments are missing ... please review the command syntax.")
        missing_args_local_recursive_error(local, recursive)

    if args_not_used_indexes:
        ERROR("too much args entered ... please review the command syntax.")
        missing_args_local_recursive_error(local, recursive)

    return dir_path_to_apply, dest_str, init_str


def missing_args_local_recursive_error(local, recursive):
    if local:
        raise ValueError("for a \"local replace\" please precise the \"initial string\", the \"destination string\" "
                         "and the \"directory path\" to apply the local replacement\na correct command would be: "
                         "replace -l titi toto /home/toto/documents/titi_folder")
    if recursive:
        raise ValueError("for a \"recursive replace\" please precise the \"initial string\", the \"destination string\" "
                         "and the \"directory path\" to apply the recursive replacement from\na "
                         "correct command would be: replace -r titi toto /home/toto/documents/titi_folder")


def get_final_parms_specific(file_paths_to_apply, dest_str, init_str,
                            specific, input_parms, args_not_used_indexes):
    if init_str is None:
        if not args_not_used_indexes:
            ERROR("arguments are missing ... please review the command syntax.")
            missing_args_specific_error(specific)

        init_str = input_parms[args_not_used_indexes[0]]
        args_not_used_indexes.pop(0)

    if dest_str is None:
        if not args_not_used_indexes:
            ERROR("arguments are missing ... please review the command syntax.")
            missing_args_specific_error(specific)

        dest_str = input_parms[args_not_used_indexes[0]]
        args_not_used_indexes.pop(0)

    if not file_paths_to_apply:
        if not args_not_used_indexes:
            ERROR("arguments are missing ... please review the command syntax.")
            missing_args_specific_error(specific)
        for parameter_not_already_used_index in args_not_used_indexes:
            file_paths_to_apply.append(input_parms[parameter_not_already_used_index])
        args_not_used_indexes = []

    if args_not_used_indexes:
        ERROR("too much args entered ... please review the command syntax.")
        missing_args_specific_error(specific)

    return file_paths_to_apply, dest_str, init_str


def missing_args_specific_error(specific):
    if specific:
        raise ValueError("for a \"specific replace\" please precise the \"initial string\", "
                         "the \"destination string\" and the \"list files paths\" to apply "
                         "the specific replacement\na correct command would be: "
                         "replace -s titi toto /home/toto/documents/test00 "
                         "documents/titi_folder/test01 documents/titi_folder/secret_titi_folder/test02")


def check_init_str_in_file(file_path, init_str, case_sensitive):

    try:
        if case_sensitive:
            for line in open(file_path, 'r', encoding=ENCODING_INPUT_FILES):
                if init_str in line:
                    return True
            return False
        elif not case_sensitive:
            for line in open(file_path, 'r', encoding=ENCODING_INPUT_FILES):
                if caseless_str1_in_str2(init_str, line):
                    return True
            return False

    except PermissionError:
        WARNING("\tyou don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CBASE)
        skipped()
        return False
    except UnicodeDecodeError:
        WARNING("\tthe file " + CFILE_PATHS + "%s" % file_path + CBASE + " owns non unicode characters")
        skipped()
        return False
    except:
        raise ValueError("the file %s seems to cause problem to be opened" % file_path)


def get_str_positions_in_lines(string, line, case_sensitive):
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


def OK(msg=""):
    print(CBGREEN + "\n\t[OK] " + CBASE + msg)


def INFO(msg=""):
    print(CBWHITE + "\n\t[INFO] " + CBASE + msg)


def WARNING(msg=""):
    print(CBORANGE + "\n\t[WARNING] " + CBASE + msg)


def ERROR(msg=""):
    print(CBRED + "\n\t[ERROR] " + CBASE + msg)


def skipped():
    print(CBBLUE + "\n\t\t\tskipped\n\n" + CBASE)


def check_user_rights(file_path):
    current_user = getpass.getuser()
    owner_file = getpwuid(stat(file_path).st_uid).pw_name
    if owner_file != current_user:
        WARNING("the file " + CFILE_PATHS + "%s" % file_path + CBASE + " is owned by " + CFILE_PATHS + "%s" % owner_file + CBASE + ", might be necessary to manage its permissions")


def print_prev_lines(previous_lines, line_nb):
    if len(previous_lines) == 2:
        print(CBYELLOW + "\t    %s: " % (line_nb - 2) + CTEXT_FILES + "%s" % previous_lines[1], end='')
        print(CBYELLOW + "\t    %s: " % (line_nb - 1) + CTEXT_FILES + "%s" % previous_lines[0] + CBASE, end='')
    elif len(previous_lines) == 1:
        print(CBYELLOW + "\t    %s: " % (line_nb - 1) + CTEXT_FILES + "%s" % previous_lines[0] + CBASE, end='')


def display_line_highlighting_init_strs(line, line_nb, start_string_positions, init_str, previous_lines):
    if len(start_string_positions) > 1:
        INFO("\n\tthere are several occurrences of " + COCCURRENCES + "\"%s\"" % init_str + CBASE + " in this line:\n")

    print_prev_lines(previous_lines, line_nb)

    print(COCCURRENCES + "\t    %s: " % line_nb + CTEXT_FILES + "%s" % line[0:start_string_positions[0]], end='')
    for string_list_index, string_index in enumerate(start_string_positions):
        print(COCCURRENCES + "%s" % init_str + CBASE, end='')
        if string_list_index == len(start_string_positions) - 1:
            print(CTEXT_FILES + "%s" % line[string_index + len(init_str):] + CBASE, end='')
        else:
            print(CTEXT_FILES + "%s" % line[string_index + len(init_str):start_string_positions[
                string_list_index + 1]] + CBASE, end='')
    return start_string_positions


def display_line_highlighting_defined_init_str(new_line, line, init_str,
                                               defined_init_str_start_position):
    print(CTEXT_FILES + "\t\t%s" % new_line, end='')
    print(COCCURRENCES + "%s" % init_str + CBASE, end='')
    print(CTEXT_FILES + "%s" %
          line[defined_init_str_start_position + len(init_str):] + CBASE, end='')


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
    print(CBYELLOW + "\n\n\t\t\taborted ...\n\t\t\t\tSee you later\n" + CBASE)
    exit()


def complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                      start_string_positions, len_init_str):
    if start_string_index == nb_occurrences_in_line - 1:
        new_line += line[start_string_position + len_init_str:]
    else:
        new_line += line[start_string_position + len_init_str:start_string_positions[start_string_index + 1]]
    return new_line


def build_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                   start_string_positions, init_str):
    new_line += init_str
    new_line = complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                 start_string_position,
                                 start_string_positions, len(init_str))
    return new_line


def multi_replacement_on_same_line(line, start_string_positions, init_str, dest_str,
                                   nb_occs_replaced, current_file, temporary_file_path, skip_file):
    new_line = line[:start_string_positions[0]]
    nb_occurrences_in_line = len(start_string_positions)

    for start_string_index, start_string_position in enumerate(start_string_positions):

        if skip_file:
            new_line = build_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                                      start_string_positions, init_str)
        else:
            print(CBYELLOW + "\n\toccurrence %s:" % (start_string_index+1) + CBASE)
            display_line_highlighting_defined_init_str(new_line, line, init_str, start_string_position)
            replace_confirmation = input("\n\tperform replacement for this occurrence?\n\t\t[Enter] to "
                                         "proceed\t\t[fF] to skip the rest of the file\n\t\t[oO] to "
                                         "skip this occurrence\t[aA] to abort the replace process\n\t")
            if replace_confirmation == "":

                print(CFILE_PATHS + "\t\t\tdone\n\n" + CBASE)
                new_line += dest_str
                new_line = complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                             start_string_position,
                                             start_string_positions, len(init_str))

                nb_occs_replaced += 1
            elif replace_confirmation in ["a", "A"]:
                abort_process(current_file, temporary_file_path)
            else:
                new_line = build_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                          start_string_position, start_string_positions, init_str)
                skipped()

            if replace_confirmation in ["f", "F"]:
                skip_file = True

    current_file.write(new_line)
    return nb_occs_replaced, skip_file


def replace_one_occurrence_asked(replace_confirmation, current_file, temporary_file_path, init_str,
                                 dest_str, line, nb_occs_replaced, case_sensitive, skip_file):
    if replace_confirmation == "":
        if case_sensitive:
            current_file.write(re.sub(init_str, dest_str, line))
        else:
            current_file.write(re.sub(init_str, dest_str, line, flags=re.I))
        nb_occs_replaced += 1
        print(CFILE_PATHS + "\t\t\tdone\n\n" + CBASE)
    elif replace_confirmation in ["a", "A"]:
        abort_process(current_file, temporary_file_path)
    else:
        current_file.write(line)
        skipped()
    if replace_confirmation in ["f", "F"]:
        skip_file = True
    return nb_occs_replaced, skip_file


def update_previous_lines(previous_lines, line):
    if len(previous_lines) == 0:
        previous_lines.append(copy.deepcopy(line))

    elif len(previous_lines) == 1:
        previous_lines.append(copy.deepcopy(previous_lines[0]))
    elif len(previous_lines) == 2:
        previous_lines[1] = copy.deepcopy(previous_lines[0])
        previous_lines[0] = copy.deepcopy(line)
    else:
        ERROR("previous lines can not have more than 2 lines, check %s" % previous_lines)
        raise ValueError("check previous lines: %s" % previous_lines)


def find_tmp_file_not_existing(file_path):
    for i in range(9):
        temporary_file_path = file_path + ".rp0" + str(i+1) + ".tmp"
        if not os.path.exists(temporary_file_path):
            return temporary_file_path
    raise ValueError("all the available tmp extensions are used for the %s path" % file_path)


def file_replace(file_path, temporary_file_path, init_str, dest_str, nb_occs_found,
                 nb_occs_replaced, ask_replace, case_sensitive, file_mask):

    current_file = open(temporary_file_path, "w")
    if not os.path.isfile(file_path):
        ERROR("the file %s doesn't exist" % file_path)
        return nb_occs_replaced

    print("\nthere is " + COCCURRENCES + "\"%s\"" % init_str + CBASE + " in the file " + CFILE_PATHS + "%s" % file_path + CBASE)
    print("\treplacing " + COCCURRENCES + "\"%s\"" % init_str + CBASE +
          " by " + COCCURRENCES + "\"%s\"" % dest_str + CBASE +
          " in " + CFILE_PATHS + "%s" % file_path + CBASE + " for the following lines:")

    previous_lines = []
    skip_file = False

    for line_index, line in enumerate(open(file_path, encoding=ENCODING_INPUT_FILES)):
        line_nb = line_index + 1
        if case_sensitive:
            if init_str in line and not skip_file:
                start_string_positions = get_str_positions_in_lines(init_str, line, case_sensitive)
                display_line_highlighting_init_strs(line, line_nb, start_string_positions, init_str,
                                                    previous_lines)
                nb_occs_found += len(start_string_positions)
                if not ask_replace:
                    nb_occs_replaced += len(start_string_positions)
                    current_file.write(re.sub(init_str, dest_str, line))
                elif ask_replace:
                    if len(start_string_positions) == 1:
                        replace_confirmation = input("\n\tperform replacement?\n\t\t[Enter] to proceed\t\t[fF] to "
                                                     "skip the rest of the file\n\t\t[oO] to skip "
                                                     "this occurrence\t[aA] to abort the replace process\n\t")

                        nb_occs_replaced, skip_file = replace_one_occurrence_asked(replace_confirmation,
                                                                                          current_file,
                                                                                          temporary_file_path,
                                                                                          init_str,
                                                                                          dest_str, line,
                                                                                          nb_occs_replaced,
                                                                                          case_sensitive, skip_file)
                    else:
                        nb_occs_replaced, skip_file = multi_replacement_on_same_line(line,
                                                                                            start_string_positions,
                                                                                            init_str,
                                                                                            dest_str,
                                                                                            nb_occs_replaced,
                                                                                            current_file,
                                                                                            temporary_file_path,
                                                                                            skip_file)

                else:
                    ERROR("the ask_replace parameter can only be \"True\" or \"False\"")
                    raise ValueError("the ask_replace parameter can not be %s" % ask_replace)
            else:
                current_file.write(line)

        elif not case_sensitive:
            if caseless_str1_in_str2(init_str, line) and not skip_file:
                start_string_positions = get_str_positions_in_lines(init_str, line, case_sensitive)
                display_line_highlighting_init_strs(line, line_nb, start_string_positions,
                                                    init_str, previous_lines)
                nb_occs_found += len(start_string_positions)
                if not ask_replace:
                    nb_occs_replaced += len(start_string_positions)
                    current_file.write(re.sub(init_str, dest_str, line, flags=re.I))
                elif ask_replace:

                    if len(start_string_positions) == 1:
                        replace_confirmation = input("\n\tperform replacement?\n\t\t[Enter] to proceed\t\t[fF] to "
                                                     "skip the rest of the file\n\t\t[oO] to skip "
                                                     "this occurrence\t[aA] to abort the replace process\n\t")

                        nb_occs_replaced, skip_file = replace_one_occurrence_asked(replace_confirmation,
                                                                                          current_file,
                                                                                          temporary_file_path,
                                                                                          init_str,
                                                                                          dest_str, line,
                                                                                          nb_occs_replaced,
                                                                                          case_sensitive, skip_file)

                    else:
                        nb_occs_replaced, skip_file = multi_replacement_on_same_line(line,
                                                                                            start_string_positions,
                                                                                            init_str,
                                                                                            dest_str,
                                                                                            nb_occs_replaced,
                                                                                            current_file,
                                                                                            temporary_file_path,
                                                                                            skip_file)
                else:
                    ERROR("the ask_replace parameter can only be \"True\" or \"False\"")
                    raise ValueError("the ask_replace parameter can not be %s" % ask_replace)
            else:
                current_file.write(line)

        else:
            ERROR("the case_sensitive parameter can only be \"True\" or \"False\"")
            raise ValueError("the case_sensitive parameter can not be %s" % case_sensitive)

        update_previous_lines(previous_lines, line)

    current_file.close()
    os.remove(file_path)
    os.rename(temporary_file_path, file_path)
    os.chmod(file_path, int(file_mask, 8))

    return nb_occs_found, nb_occs_replaced


def check_file_extension_in_blacklist(file_path):
    for black_list_extension in BLACK_LIST_EXTENSIONS_LIST:
        if file_path.endswith(black_list_extension):
            WARNING("the file %s owns the extension %s that is not accepted by default\n\t"
                    "use one of these parameters %s if you want to perform replacement in this kind of file "
                    "anyway" % (file_path, black_list_extension, NO_BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS))
            skipped()
            return True
    return False


def check_filename_must_end_by(filename_must_end_by, file_path):
    for acceptable_filename_end in filename_must_end_by:
        if file_path.endswith(acceptable_filename_end):
            return True
    WARNING("the file %s doesn't end by the acceptable end extensions you entered: %s" % (file_path, filename_must_end_by))
    skipped()
    return False


def check_file_owns_excluded_path(excluded_paths, file_path):
    for excluded_path in excluded_paths:
        if file_path.startswith(excluded_path):
            WARNING("the file %s is excluded regarding the excluded path %s you entered" % (file_path, excluded_path))
            skipped()
            return True
    return False


def check_file_owns_excluded_extension(excluded_extensions, file_path):
    for excluded_extension in excluded_extensions:
        if file_path.endswith(excluded_extension):
            WARNING("the file %s is excluded regarding the excluded extension %s you entered" % (file_path, excluded_extension))
            skipped()
            return True
    return False


def check_file_owns_excluded_string(excluded_strings, file_path):
    for excluded_string in excluded_strings:
        if excluded_string in file_path:
            WARNING("the file %s is excluded regarding the excluded string %s you entered" % (file_path, excluded_string))
            skipped()
            return True
    return False


def check_able_open_file(file_path):

    try:
        open_test = open(file_path, 'r', encoding=ENCODING_INPUT_FILES)
        open_test.close()
        return True
    except FileNotFoundError:
        ERROR("the file " + CFILE_PATHS + "%s" % file_path + CBASE + " doesn't exist")
        skipped()
        return False
    except PermissionError:
        ERROR("you don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CBASE)
        skipped()
        return False
    except IsADirectoryError:
        ERROR("the path " + CFILE_PATHS + "%s" % file_path + CBASE + "is a directory, not a file")
        skipped()
        return False
    except OSError:
        ERROR("no such device or address " + CFILE_PATHS + "%s" % file_path + CBASE)
        skipped()
        return False


def check_able_create_temporary(temporary_file_path, file_mask):

    try:
        open_test = open(temporary_file_path, 'w+')
        open_test.close()
        os.chmod(temporary_file_path, int(file_mask, 8))
        os.remove(temporary_file_path)
        return True
    except FileNotFoundError:
        ERROR("the file " + CFILE_PATHS + "%s" % temporary_file_path + CBASE + " doesn't exist")
        skipped()
        return False
    except PermissionError:
        ERROR("you don't have the permission to create the file " + CFILE_PATHS + "%s" % temporary_file_path + CBASE)
        skipped()
        return False
    except IsADirectoryError:
        ERROR(" the path " + CFILE_PATHS + "%s" % temporary_file_path + CBASE + "is a directory, not a file")
        skipped()
        return False


def check_binary_file(file_path):
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    try:
        if is_binary_string(open(file_path, 'rb').read(1024)):
            WARNING("the file %s is a binary file" % file_path)
            skipped()
            return True
        return False
    except PermissionError:
        ERROR("you don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CBASE)
        skipped()
        return True


def check_symlink_path(file_path):
    if os.path.islink(file_path):
        WARNING("the file %s is a symlink file" % file_path)
        skipped()
        return True
    return False


def get_temporary_file_path(file_path, excluded_paths):
    temporary_file_path = file_path + ".tmp"
    if os.path.exists(temporary_file_path):
        temporary_file_path = find_tmp_file_not_existing(file_path)
    excluded_paths.append(temporary_file_path)
    return temporary_file_path


def get_file_permission_mask(file_path):
    return oct(os.stat(file_path).st_mode & 0o777)


def replace_local_recursive(directory_path, init_str, dest_str, black_list_extensions,
                            filename_must_end_by, excluded_paths, excluded_strings, excluded_extensions, local,
                            nb_occs_found, nb_occs_replaced, ask_replace, case_sensitive, binary_accepted,
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
                WARNING("the file path " + CFILE_PATHS + "%s" % file_path + CBASE + " seems to cause problem, might be a broken simlink")
                continue

            check_user_rights(file_path)
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

            temporary_file_path = get_temporary_file_path(file_path, excluded_paths)
            if not check_able_create_temporary(temporary_file_path, file_mask):
                continue

            if check_init_str_in_file(file_path, init_str, case_sensitive):
                nb_occs_found, nb_occs_replaced = file_replace(file_path, temporary_file_path,
                                                                             init_str, dest_str,
                                                                             nb_occs_found,
                                                                             nb_occs_replaced,
                                                                             ask_replace, case_sensitive, file_mask)
        if local:
            break
    return nb_occs_found, nb_occs_replaced


def check_folder_path_exists(folderpath):
    if not os.path.isdir(folderpath):
        WARNING(CFILE_PATHS + " %s " % folderpath + CBASE + "folder doesn't exist")
        raise ValueError("the directory path to apply %s doesn't exist, you may review it" % folderpath)


def check_path_exists(path):
    if not os.path.exists(path):
        WARNING(CFILE_PATHS + " %s " % path + CBASE + "path doesn't exist")
        return False
    return True


def replace_specific(file_paths_to_apply, init_str, dest_str,
                     nb_occs_found, nb_occs_replaced, black_list_extensions, ask_replace, case_sensitive,
                     binary_accepted, symlink_accepted):
    for file_path in file_paths_to_apply:

        if not check_path_exists(file_path):
            WARNING("the file path %s seems to cause problem, might be a broken simlink" % file_path)
            skipped()
            continue

        check_user_rights(file_path)
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
        temporary_file_path = get_temporary_file_path(file_path, [])
        if not check_able_create_temporary(temporary_file_path, file_mask):
            continue

        if check_init_str_in_file(file_path, init_str, case_sensitive):
            nb_occs_found, nb_occs_replaced = file_replace(file_path, temporary_file_path, init_str,
                                                   dest_str, nb_occs_found,
                                                   nb_occs_replaced, ask_replace, case_sensitive, file_mask)
    return nb_occs_found, nb_occs_replaced


def occs_summary(nb_occs_found, nb_occs_replaced, init_str):
    if nb_occs_found == 0:
        print(CFILE_PATHS + "\n\t0" + CBASE + " occurrence of " + COCCURRENCES + "%s" % init_str + CBASE + " found")
    elif nb_occs_found == 1:
        print(CFILE_PATHS + "\n\t1" + CBASE + " occurrence of " + COCCURRENCES + "%s" % init_str +
              CBASE + " found and " + CFILE_PATHS + "%s" % nb_occs_replaced + CBASE + " replaced")
    else:
        print(CFILE_PATHS + "\n\t%s" % nb_occs_found + CBASE + " occurrences of " + COCCURRENCES +
              "%s" % init_str + CBASE + " found and " + CFILE_PATHS + "%s" % nb_occs_replaced +
              CBASE + " replaced")


def get_full_paths(dir_path_to_apply, file_paths_to_apply):
    if file_paths_to_apply:
        filepaths_list = []

        for filename in file_paths_to_apply:
            filepaths_list.append(get_full_path_joined(filename))

        file_paths_to_apply = filepaths_list

    if dir_path_to_apply is not None:
        dir_path_to_apply = get_full_path_joined(dir_path_to_apply)

    return dir_path_to_apply, file_paths_to_apply


def get_full_path_joined(given_path):
    return os.path.normpath((os.path.join(os.getcwd(), os.path.expanduser(given_path))))


def check_integrity_of_mode_request(local, recursive, specific, dir_path_to_apply, file_paths_to_apply):
    if local or recursive:
        if file_paths_to_apply:
            WARNING("the replace mode is not specific, file_paths_to_apply should be empty and is: %s" % file_paths_to_apply)
            raise ValueError("file_paths_to_apply should be empty")
        if dir_path_to_apply is None:
            WARNING("the replace mode is not specific, dir_path_to_apply should not be None")
            raise ValueError("dir_path_to_apply should be defined")
        if not check_path_exists(dir_path_to_apply):
            raise ValueError("the directory path %s doesn't exist" % dir_path_to_apply)
        if not os.path.isdir(dir_path_to_apply):
            INFO(CFILE_PATHS + "%s" + CBASE + " is a file, proceeding specific replace mode" % dir_path_to_apply)
            local = False
            recursive = False
            specific = True
            file_paths_to_apply.append(dir_path_to_apply)

    elif specific:
        if not file_paths_to_apply:
            ERROR("the replace mode is specific, file_paths_to_apply should not be empty and is: %s" % file_paths_to_apply)
            raise ValueError("file_paths_to_apply should not be empty in specific mode replacement")
        if dir_path_to_apply is not None:
            ERROR("the replace mode is specific, dir_path_to_apply should be None")
            raise ValueError("dir_path_to_apply should not be defined")

        file_paths = []
        for filepath in file_paths_to_apply:
            if not check_path_exists(filepath):
                WARNING(CFILE_PATHS + "%s" + CBASE + " doesn't exist, removing it from the file list" % filepath)
            elif os.path.isdir(filepath):
                WARNING(CFILE_PATHS + "%s" + CBASE + " is a folder, removing it from the file list" % filepath)
            else:
                file_paths.append(filepath)

        file_paths_to_apply = file_paths
    return local, recursive, specific, dir_path_to_apply, file_paths_to_apply


def main():

    input_parms = sys.argv[1:]
    check_help_request(input_parms)
    check_nb_parameters(input_parms)
    filename_must_end_by, local, recursive, specific, ask_replace, case_sensitive, \
        black_list_extensions, binary_accepted, symlink_accepted, excluded_strings, \
        excluded_extensions, excluded_paths = initiate_indicators_values()

    init_str, dest_str, dir_path_to_apply, file_paths_to_apply, \
        nb_occs_found, nb_occs_replaced = initiate_args_values()

    filename_must_end_by, init_str, dest_str, dir_path_to_apply, file_paths_to_apply, \
        local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, binary_accepted, \
        symlink_accepted, excluded_strings, excluded_extensions, excluded_paths, args_not_used_indexes = \
        treat_input_parms(input_parms, filename_must_end_by, init_str, dest_str,
                               dir_path_to_apply, file_paths_to_apply, local, recursive, specific,
                               ask_replace, case_sensitive, black_list_extensions, binary_accepted, symlink_accepted,
                               excluded_strings, excluded_extensions, excluded_paths)

    check_only_one_replace_mode_picked(local, specific, recursive)

    # finalize getting all the parameters
    if local or recursive:
        dir_path_to_apply, dest_str, init_str = \
            get_final_parms_local_recursive(dir_path_to_apply, dest_str,
                                                              init_str, local, recursive, input_parms,
                                                              args_not_used_indexes)

    elif specific:
        file_paths_to_apply, dest_str, init_str = \
            get_final_parms_specific(file_paths_to_apply, dest_str,
                                                       init_str, specific, input_parms,
                                                       args_not_used_indexes)
    else:
        ERROR("the replace mode can only be \"local\", \"recursive\" or \"specific\"")
        raise ValueError("please pick only one mode with the -l, -r or -s short options")

    dir_path_to_apply, file_paths_to_apply = get_full_paths(dir_path_to_apply, file_paths_to_apply)
    local, recursive, specific, dir_path_to_apply, file_paths_to_apply = check_integrity_of_mode_request(
        local, recursive, specific, dir_path_to_apply, file_paths_to_apply)

    # apply the replace
    if local:
        nb_occs_found, nb_occs_replaced = \
            replace_local_recursive(dir_path_to_apply, init_str, dest_str, black_list_extensions,
                                    filename_must_end_by, excluded_paths, excluded_strings, excluded_extensions, local,
                                    nb_occs_found, nb_occs_replaced, ask_replace, case_sensitive,
                                    binary_accepted, symlink_accepted)

    elif recursive:
        nb_occs_found, nb_occs_replaced = \
            replace_local_recursive(dir_path_to_apply, init_str, dest_str, black_list_extensions,
                                    filename_must_end_by, excluded_paths, excluded_strings, excluded_extensions, local,
                                    nb_occs_found, nb_occs_replaced, ask_replace, case_sensitive,
                                    binary_accepted, symlink_accepted)

    elif specific:
        nb_occs_found, nb_occs_replaced = \
            replace_specific(file_paths_to_apply, init_str, dest_str,
                             nb_occs_found, nb_occs_replaced, black_list_extensions, ask_replace,
                             case_sensitive, binary_accepted, symlink_accepted)
    else:
        ERROR("the replace mode can only be \"local\", \"recursive\" or \"specific\"")
        raise ValueError("please pick only one mode with the -l, -r or -s short options")

    occs_summary(nb_occs_found, nb_occs_replaced, init_str)


if __name__ == "__main__":
    main()
