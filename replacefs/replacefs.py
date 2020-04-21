#!/usr/bin/python

import os
import re
import sys
import getpass
import unicodedata
import copy

from os import stat
from pwd import getpwuid

__author__ = 'Yann Orieult'

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
FILENAME_MUST_END_BY_INDICATORS_STRINGS = ["--file_name_must_end_by", "--end_by"]
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
AUDIO_EXTENSIONS = ["mp3", "MP3", "wav", "WAV", "m4a", "M4A", "aac", "AAC", "mp1", "MP1", "mp2", "MP2", "mpg", "MPG",
                    "flac", "FLAC"]
IMAGE_EXTENSIONS = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG", "tif", "TIF", "gif", "GIF", "bmp", "BMP", "pjpeg",
                    "PJPEG"]
VIDEO_EXTENSIONS = ["mp4", "MP4", "mpeg", "MPEG", "avi", "AVI", "wma", "WMA", "ogg", "OGG", "quicktime", "QUICKTIME",
                    "webm", "WEBM", "mp2t", "MP2T", "flv", "FLV", "mov", "MOV", "webm", "WEBM", "mkv", "MKV"]
PROGRAMMING_EXTENSIONS = ["class", "CLASS"]

BLACK_LIST_EXTENSIONS_LIST = AUDIO_EXTENSIONS + IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + PROGRAMMING_EXTENSIONS

# supported short indicators
SUPPORTED_SHORT_INDICATORS = ['l', 'r', 's', 'a', 'c']


def _help_requested(arguments):
    if len(arguments) == 1 and (arguments[0] == "-h" or arguments[0] == "--help"):
        README_path = "/usr/lib/replace/README.md"

        f = open(README_path, 'r')
        print(CFILE_PATHS + "\n\t#######      replace documentation      #######\n" + CBWHITE)

        for line in f:
            if line == "```sh\n" or line == "```\n" or line == "<pre>\n" or line == "</pre>\n":
                continue

            line = line.replace('```sh', '').replace('```', '').replace('<pre>', '').replace('</b>', ''). \
                replace('<b>', '').replace('<!-- -->', '').replace('<br/>', '').replace('```sh', ''). \
                replace('***', '').replace('***', '').replace('**', '').replace('*', '')

            print(" " + line, end='')
        print(CBASE)
        exit()


def _check_input_args(args):
    if len(args) < 2:
        _error("not enough arguments, needs at least the initial string and the destination string\n\tneeds the "
               "replace mode (-l -r or -s), the initial string, the destination string and the path to process"
               "\n\ta typical example would be: " + CBWHITE + "replace -l dog cat ." + CBASE)
        exit(1)


def _init_indicators():
    file_name_must_end_by = []
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
    return file_name_must_end_by, local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, + \
        binary_accepted, symlink_accepted, excluded_strings, excluded_extensions, excluded_paths


def _init_args():
    init_str = None
    dest_str = None
    dir_path_to_apply = None
    file_paths_to_apply = []
    nb_occs_found = 0
    nb_occs_replaced = 0
    return init_str, dest_str, dir_path_to_apply, file_paths_to_apply, nb_occs_found, nb_occs_replaced


def _treat_input_args(input_args, file_name_must_end_by, init_str,
                      dest_str, dir_path_to_apply, file_paths_to_apply,
                      local, recursive, specific, ask_replace, case_sensitive, black_list_extensions,
                      binary_accepted, symlink_accepted, excluded_strings, excluded_extensions, excluded_paths):
    nb_args = len(input_args)
    not_compatible_shorts_indicators = []
    args_not_used_indexes = list(range(nb_args))
    for arg_index, arg in enumerate(input_args):
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
                        for potential_end_filter_index, potential_end_filter in enumerate(input_args[arg_index + 1:]):
                            if not potential_end_filter.startswith("-"):
                                file_name_must_end_by.append(potential_end_filter)
                                args_not_used_indexes.remove(arg_index + 1 + potential_end_filter_index)
                            else:
                                break
                    elif arg in EXCLUDED_PATHS_INDICATORS_STRINGS:
                        for potential_file_path_to_exclude_index, potential_file_path_to_exclude in enumerate(
                                input_args[arg_index + 1:]):
                            if not potential_file_path_to_exclude.startswith("-"):
                                potential_file_path_to_exclude = get_full_path_joined(potential_file_path_to_exclude)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_file_path_to_exclude_index)

                                if _check_path_exists(potential_file_path_to_exclude):
                                    excluded_paths.append(potential_file_path_to_exclude)
                            else:
                                break

                    elif arg in ADD_EXCLUDED_EXTENSIONS_INDICATORS_STRINGS:
                        for potential_new_excluded_extension_index, potential_new_excluded_extension in enumerate(
                                input_args[arg_index + 1:]):
                            if not potential_new_excluded_extension.startswith("-"):
                                excluded_extensions.append(potential_new_excluded_extension)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_new_excluded_extension_index)

                            else:
                                break

                    elif arg in ADD_EXCLUDED_STRINGS_INDICATORS_STRINGS:
                        for potential_new_excluded_string_index, potential_new_excluded_string in enumerate(
                                input_args[arg_index + 1:]):
                            if not potential_new_excluded_string.startswith("-"):
                                excluded_strings.append(potential_new_excluded_string)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_new_excluded_string_index)

                            else:
                                break

                    elif arg in INITIAL_STRING_INDICATORS_STRINGS:
                        init_str = input_args[arg_index + 1]
                        args_not_used_indexes.remove(arg_index + 1)
                    elif arg in DESTINATION_STRING_INDICATORS_STRINGS:
                        dest_str = input_args[arg_index + 1]
                        args_not_used_indexes.remove(arg_index + 1)
                    elif arg in DIRECTORY_PATH_TO_APPLY_INDICATORS_STRINGS:
                        dir_path_to_apply = input_args[arg_index + 1]
                        args_not_used_indexes.remove(arg_index + 1)
                    elif arg in LIST_FILES_PATHS_TO_APPLY_INDICATORS_STRINGS:
                        for potential_file_path_to_replace_index, potential_file_path_to_replace in enumerate(
                                input_args[arg_index + 1:]):
                            if not potential_file_path_to_replace.startswith("-"):
                                file_paths_to_apply.append(potential_file_path_to_replace)
                                args_not_used_indexes.remove(
                                    arg_index + 1 + potential_file_path_to_replace_index)
                            else:
                                break

                else:
                    _error("no parameter after %s indicator" % arg +
                           "\n\tneeds a parameter after the %s indicator" % arg)
                    exit(1)

                args_not_used_indexes.remove(arg_index)

            else:
                _error("the indicator %s is not supported" % arg +
                       "\n\tplease remove the %s parameter from the command" % arg)
                exit(1)
        elif arg.startswith("-"):
            for short_indicator in arg[1:]:
                if short_indicator not in SUPPORTED_SHORT_INDICATORS:
                    _error("the short indicator -%s is not supported" % short_indicator +
                           "\n\tplease remove the -%s short indicator from the command" % short_indicator)
                    exit(1)
                elif short_indicator in not_compatible_shorts_indicators:
                    _error("the short indicator -%s is not compatible with these short "
                           "indicators %s" % (short_indicator, not_compatible_shorts_indicators) +
                           "\n\tplease remove one of the incompatibles shorts indicators from the command")
                    exit(1)
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
    return file_name_must_end_by, init_str, dest_str, dir_path_to_apply, file_paths_to_apply, \
           local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, binary_accepted, \
           symlink_accepted, excluded_strings, excluded_extensions, excluded_paths, args_not_used_indexes


def _check_only_one_replace_mode_picked(local, specific, recursive):
    nb_of_true = 0
    for replace_mode in [local, specific, recursive]:
        if replace_mode:
            nb_of_true += 1
    if nb_of_true != 1:
        _error("the replace mode can only be \"local\", \"recursive\" or \"specific\"\n\tplease pick only one mode " +
               "with the -l, -r or -s short options")
        exit(1)


def _get_final_args_local_recursive(dir_path_to_apply, dest_str, init_str, local, recursive,
                                    input_args, args_not_used_indexes):
    if dir_path_to_apply is None:
        if not args_not_used_indexes:
            _error("arguments are missing ... please review the command syntax.")
            _args_local_recursive_error(local, recursive)

        dir_path_to_apply = input_args[args_not_used_indexes[-1]]
        args_not_used_indexes.pop()
    if dest_str is None:
        if not args_not_used_indexes:
            _error("arguments are missing ... please review the command syntax.")
            _args_local_recursive_error(local, recursive)

        dest_str = input_args[args_not_used_indexes[-1]]
        args_not_used_indexes.pop()
    if init_str is None:
        if not args_not_used_indexes:
            _error("arguments are missing ... please review the command syntax.")
            _args_local_recursive_error(local, recursive)

        init_str = input_args[args_not_used_indexes[-1]]
        args_not_used_indexes.pop()

    if dir_path_to_apply is None or dest_str is None or init_str is None:
        _error("arguments are missing ... please review the command syntax.")
        _args_local_recursive_error(local, recursive)

    if args_not_used_indexes:
        _error("too much args entered ... please review the command syntax.")
        _args_local_recursive_error(local, recursive)

    return dir_path_to_apply, dest_str, init_str


def _args_local_recursive_error(local, recursive):
    if local:
        _error("for a \"local replace\" please precise the \"initial string\", the \"destination string\" and "
               "the \"directory path\" to apply the local replacement\na correct command would be:\n\t"
               + CBWHITE + "replace -l titi toto /home/toto/documents/titi_folder" + CBASE)
        exit(1)
    if recursive:
        _error("for a \"recursive replace\" please precise the \"initial string\", the \"destination string\" and "
               "the \"directory path\" to apply the recursive replacement from\na correct command would be:\n\t"
               + CBWHITE + "replace -r titi toto /home/toto/documents/titi_folder" + CBASE)
        exit(1)


def _get_final_args_specific(file_paths_to_apply, dest_str, init_str, specific, input_args, args_not_used_indexes):
    if init_str is None:
        if not args_not_used_indexes:
            _error("arguments are missing ... please review the command syntax.")
            _args_specific_error(specific)

        init_str = input_args[args_not_used_indexes[0]]
        args_not_used_indexes.pop(0)

    if dest_str is None:
        if not args_not_used_indexes:
            _error("arguments are missing ... please review the command syntax.")
            _args_specific_error(specific)

        dest_str = input_args[args_not_used_indexes[0]]
        args_not_used_indexes.pop(0)

    if not file_paths_to_apply:
        if not args_not_used_indexes:
            _error("arguments are missing ... please review the command syntax.")
            _args_specific_error(specific)
        for parameter_not_already_used_index in args_not_used_indexes:
            file_paths_to_apply.append(input_args[parameter_not_already_used_index])
        args_not_used_indexes = []

    if args_not_used_indexes:
        _error("too much args entered ... please review the command syntax.")
        _args_specific_error(specific)

    return file_paths_to_apply, dest_str, init_str


def _args_specific_error(specific):
    if specific:
        _error("for a \"specific replace\" please precise the \"initial string\", "
               "the \"destination string\" and the \"list files paths\" to apply the specific replacement\n\t" +
               "a correct command would be: " + CBWHITE + "replace -s titi toto /home/toto/documents/test00 "
                                                          "documents/titi_folder/test01 documents/titi_"
                                                          "folder/secret_titi_folder/test02" + CBASE)
        exit(1)


def _check_init_str_in_file(file_path, init_str, case_sensitive):
    try:
        if case_sensitive:
            for line in open(file_path, 'r', encoding=ENCODING_INPUT_FILES):
                if init_str in line:
                    return True
            return False
        elif not case_sensitive:
            for line in open(file_path, 'r', encoding=ENCODING_INPUT_FILES):
                if _case_less_str1_in_str2(init_str, line):
                    return True
            return False

    except PermissionError:
        _warning("\tyou don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CBASE)
        _skipped()
        return False
    except UnicodeDecodeError:
        _warning("\tthe file " + CFILE_PATHS + "%s" % file_path + CBASE + " owns non unicode characters")
        _skipped()
        return False
    except:
        _error("the file %s seems to cause problem to be opened" % file_path)
        exit(1)


def _get_str_positions_in_lines(string, line, case_sensitive):
    start_string_indexes = []
    if case_sensitive:
        for index in range(len(line)):
            if line[index:].startswith(string):
                start_string_indexes.append(index)
    if not case_sensitive:
        for index in range(len(line)):
            if _normalize_case_less(line)[index:].startswith(_normalize_case_less(string)):
                start_string_indexes.append(index)
    return start_string_indexes


# def ok(msg=""):
#     print(CBGREEN + "\n\t[OK] " + CBASE + msg)


def _info(msg=""):
    print(CBWHITE + "\n\t[INFO] " + CBASE + msg)


def _warning(msg=""):
    print(CBORANGE + "\n\t[WARNING] " + CBASE + msg)


def _error(msg=""):
    print(CBRED + "\n\t[ERROR] " + CBASE + msg)


def _skipped():
    print(CBBLUE + "\n\t\t\tskipped\n\n" + CBASE)


def _check_user_rights(file_path):
    current_user = getpass.getuser()
    owner_file = getpwuid(stat(file_path).st_uid).pw_name
    if owner_file != current_user:
        _warning("the file " + CFILE_PATHS + "%s" % file_path + CBASE + " is owned by " + CFILE_PATHS +
                 "%s" % owner_file + CBASE + ", might be necessary to manage its permissions")


def _print_prev_lines(previous_lines, line_nb):
    if len(previous_lines) == 2:
        print(CBYELLOW + "\t    %s: " % (line_nb - 2) + CTEXT_FILES + "%s" % previous_lines[1], end='')
        print(CBYELLOW + "\t    %s: " % (line_nb - 1) + CTEXT_FILES + "%s" % previous_lines[0] + CBASE, end='')
    elif len(previous_lines) == 1:
        print(CBYELLOW + "\t    %s: " % (line_nb - 1) + CTEXT_FILES + "%s" % previous_lines[0] + CBASE, end='')


def _display_line_highlighting_init_strs(line, line_nb, start_string_positions, init_str, previous_lines):
    if len(start_string_positions) > 1:
        _info("\n\tthere are several occurrences of " + COCCURRENCES + "\"%s\"" % init_str + CBASE + " in this line:\n")

    _print_prev_lines(previous_lines, line_nb)

    print(COCCURRENCES + "\t    %s: " % line_nb + CTEXT_FILES + "%s" % line[0:start_string_positions[0]], end='')
    for string_list_index, string_index in enumerate(start_string_positions):
        print(COCCURRENCES + "%s" % init_str + CBASE, end='')
        if string_list_index == len(start_string_positions) - 1:
            print(CTEXT_FILES + "%s" % line[string_index + len(init_str):] + CBASE, end='')
        else:
            print(CTEXT_FILES + "%s" % line[string_index + len(init_str):start_string_positions[
                string_list_index + 1]] + CBASE, end='')
    return start_string_positions


def _display_line_highlighting_defined_init_str(new_line, line, init_str,
                                                defined_init_str_start_position):
    print(CTEXT_FILES + "\t\t%s" % new_line, end='')
    print(COCCURRENCES + "%s" % init_str + CBASE, end='')
    print(CTEXT_FILES + "%s" %
          line[defined_init_str_start_position + len(init_str):] + CBASE, end='')


def _normalize_case_less(string):
    return unicodedata.normalize("NFKD", string.casefold())


def _case_less_equal(str1, str2):
    return _normalize_case_less(str1) == _normalize_case_less(str2)


def _case_less_str1_in_str2(str1, str2):
    if _normalize_case_less(str1) in _normalize_case_less(str2):
        return True
    else:
        return False


def _abort_process(current_file, temporary_file_path):
    current_file.close()
    os.remove(temporary_file_path)
    print(CBYELLOW + "\n\n\t\t\taborted ...\n\t\t\t\tSee you later\n" + CBASE)
    exit()


def _complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                       start_string_positions, len_init_str):
    if start_string_index == nb_occurrences_in_line - 1:
        new_line += line[start_string_position + len_init_str:]
    else:
        new_line += line[start_string_position + len_init_str:start_string_positions[start_string_index + 1]]
    return new_line


def _build_new_line(new_line, line, start_string_index, nb_occurrences_in_line, start_string_position,
                    start_string_positions, init_str):
    new_line += init_str
    new_line = _complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                  start_string_position,
                                  start_string_positions, len(init_str))
    return new_line


def _multi_replacement_on_same_line(line, start_string_positions, init_str, dest_str,
                                    nb_occs_replaced, current_file, temporary_file_path, skip_file):
    new_line = line[:start_string_positions[0]]
    nb_occurrences_in_line = len(start_string_positions)

    for start_string_index, start_string_position in enumerate(start_string_positions):

        if skip_file:
            new_line = _build_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                       start_string_position,
                                       start_string_positions, init_str)
        else:
            print(CBYELLOW + "\n\toccurrence %s:" % (start_string_index + 1) + CBASE)
            _display_line_highlighting_defined_init_str(new_line, line, init_str, start_string_position)
            replace_conf = input("\n\tperform replacement for this occurrence?\n\t\t[Enter] to proceed\t\t[fF] to "
                                 "skip the rest of the file\n\t\t[oO] to skip this occurrence\t[aA] to abort "
                                 "the replace process\n\t")
            if replace_conf == "":

                print(CFILE_PATHS + "\t\t\tdone\n\n" + CBASE)
                new_line += dest_str
                new_line = _complete_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                              start_string_position,
                                              start_string_positions, len(init_str))

                nb_occs_replaced += 1
            elif replace_conf in ["a", "A"]:
                _abort_process(current_file, temporary_file_path)
            else:
                new_line = _build_new_line(new_line, line, start_string_index, nb_occurrences_in_line,
                                           start_string_position, start_string_positions, init_str)
                _skipped()

            if replace_conf in ["f", "F"]:
                skip_file = True

    current_file.write(new_line)
    return nb_occs_replaced, skip_file


def _replace_one_occurrence_asked(replace_conf, current_file, temporary_file_path, init_str,
                                  dest_str, line, nb_occs_replaced, case_sensitive, skip_file):
    if replace_conf == "":
        if case_sensitive:
            current_file.write(re.sub(init_str, dest_str, line))
        else:
            current_file.write(re.sub(init_str, dest_str, line, flags=re.I))
        nb_occs_replaced += 1
        print(CFILE_PATHS + "\t\t\tdone\n\n" + CBASE)
    elif replace_conf in ["a", "A"]:
        _abort_process(current_file, temporary_file_path)
    else:
        current_file.write(line)
        _skipped()
    if replace_conf in ["f", "F"]:
        skip_file = True
    return nb_occs_replaced, skip_file


def _update_previous_lines(previous_lines, line):
    if len(previous_lines) == 0:
        previous_lines.append(copy.deepcopy(line))

    elif len(previous_lines) == 1:
        previous_lines.append(copy.deepcopy(previous_lines[0]))
    elif len(previous_lines) == 2:
        previous_lines[1] = copy.deepcopy(previous_lines[0])
        previous_lines[0] = copy.deepcopy(line)
    else:
        _error("previous lines can not have more than 2 lines, check %s" % previous_lines)
        exit(1)


def _find_tmp_file_not_existing(file_path):
    for i in range(9):
        temporary_file_path = file_path + ".rp0" + str(i + 1) + ".tmp"
        if not os.path.exists(temporary_file_path):
            return temporary_file_path
    _error("all the available tmp extensions are used for the %s path" % file_path)
    exit(1)


def _file_replace(file_path, temporary_file_path, init_str, dest_str, nb_occs_found,
                  nb_occs_replaced, ask_replace, case_sensitive, file_mask):
    current_file = open(temporary_file_path, "w")
    if not os.path.isfile(file_path):
        _error("the file %s doesn't exist" % file_path)
        return nb_occs_replaced

    print("\nthere is " + COCCURRENCES + "\"%s\"" % init_str + CBASE + " in the file " +
          CFILE_PATHS + "%s" % file_path + CBASE)
    print("\treplacing " + COCCURRENCES + "\"%s\"" % init_str + CBASE +
          " by " + COCCURRENCES + "\"%s\"" % dest_str + CBASE +
          " in " + CFILE_PATHS + "%s" % file_path + CBASE + " for the following lines:")

    previous_lines = []
    skip_file = False

    for line_index, line in enumerate(open(file_path, encoding=ENCODING_INPUT_FILES)):
        line_nb = line_index + 1
        if case_sensitive:
            if init_str in line and not skip_file:
                start_string_positions = _get_str_positions_in_lines(init_str, line, case_sensitive)
                _display_line_highlighting_init_strs(line, line_nb, start_string_positions, init_str,
                                                     previous_lines)
                nb_occs_found += len(start_string_positions)
                if not ask_replace:
                    nb_occs_replaced += len(start_string_positions)
                    current_file.write(re.sub(init_str, dest_str, line))
                elif ask_replace:
                    if len(start_string_positions) == 1:
                        replace_conf = input("\n\tperform replacement?\n\t\t[Enter] to proceed\t\t[fF] to skip "
                                             "the rest of the file\n\t\t[oO] to skip this occurrence\t"
                                             "[aA] to abort the replace process\n\t")

                        nb_occs_replaced, skip_file = _replace_one_occurrence_asked(replace_conf,
                                                                                    current_file,
                                                                                    temporary_file_path,
                                                                                    init_str,
                                                                                    dest_str, line,
                                                                                    nb_occs_replaced,
                                                                                    case_sensitive, skip_file)
                    else:
                        nb_occs_replaced, skip_file = _multi_replacement_on_same_line(line,
                                                                                      start_string_positions,
                                                                                      init_str,
                                                                                      dest_str,
                                                                                      nb_occs_replaced,
                                                                                      current_file,
                                                                                      temporary_file_path,
                                                                                      skip_file)

                else:
                    _error("the ask_replace parameter can only be \"True\" or \"False\"" +
                           "the ask_replace parameter can not be %s" % ask_replace)
                    exit(1)
            else:
                current_file.write(line)

        elif not case_sensitive:
            if _case_less_str1_in_str2(init_str, line) and not skip_file:
                start_string_positions = _get_str_positions_in_lines(init_str, line, case_sensitive)
                _display_line_highlighting_init_strs(line, line_nb, start_string_positions,
                                                     init_str, previous_lines)
                nb_occs_found += len(start_string_positions)
                if not ask_replace:
                    nb_occs_replaced += len(start_string_positions)
                    current_file.write(re.sub(init_str, dest_str, line, flags=re.I))
                elif ask_replace:

                    if len(start_string_positions) == 1:
                        replace_conf = input("\n\tperform replacement?\n\t\t[Enter] to proceed\t\t[fF] to skip "
                                             "the rest of the file\n\t\t[oO] to skip this occurrence\t[aA] to abort "
                                             "the replace process\n\t")

                        nb_occs_replaced, skip_file = _replace_one_occurrence_asked(replace_conf,
                                                                                    current_file,
                                                                                    temporary_file_path,
                                                                                    init_str,
                                                                                    dest_str, line,
                                                                                    nb_occs_replaced,
                                                                                    case_sensitive, skip_file)

                    else:
                        nb_occs_replaced, skip_file = _multi_replacement_on_same_line(line,
                                                                                      start_string_positions,
                                                                                      init_str,
                                                                                      dest_str,
                                                                                      nb_occs_replaced,
                                                                                      current_file,
                                                                                      temporary_file_path,
                                                                                      skip_file)
                else:
                    _error("the ask_replace parameter can only be \"True\" or \"False\"" +
                           "the ask_replace parameter can not be %s" % ask_replace)
                    exit(1)
            else:
                current_file.write(line)

        else:
            _error("the case_sensitive parameter can only be \"True\" or \"False\"" +
                   "the case_sensitive parameter can not be %s" % case_sensitive)
            exit(1)

        _update_previous_lines(previous_lines, line)

    current_file.close()
    os.remove(file_path)
    os.rename(temporary_file_path, file_path)
    os.chmod(file_path, int(file_mask, 8))

    return nb_occs_found, nb_occs_replaced


def _check_file_extension_in_blacklist(file_path):
    for black_list_extension in BLACK_LIST_EXTENSIONS_LIST:
        if file_path.endswith(black_list_extension):
            _warning("the file %s owns the extension %s that is not accepted by default\n\t"
                     "use one of these parameters %s if you want to perform replacement in this kind of file "
                     "anyway" % (file_path, black_list_extension, NO_BLACK_LIST_EXTENSIONS_INDICATORS_STRINGS))
            _skipped()
            return True
    return False


def _check_file_name_must_end_by(file_name_must_end_by, file_path):
    for acceptable_file_name_end in file_name_must_end_by:
        if file_path.endswith(acceptable_file_name_end):
            return True
    _warning(
        "the file %s doesn't end by the acceptable end extensions you entered: %s" % (file_path, file_name_must_end_by))
    _skipped()
    return False


def _check_file_owns_excluded_path(excluded_paths, file_path):
    for excluded_path in excluded_paths:
        if file_path.startswith(excluded_path):
            _warning("the file %s is excluded regarding the excluded path %s you entered" % (file_path, excluded_path))
            _skipped()
            return True
    return False


def _check_file_owns_excluded_extension(excluded_extensions, file_path):
    for excluded_extension in excluded_extensions:
        if file_path.endswith(excluded_extension):
            _warning("the file %s is excluded regarding the "
                     "excluded extension %s you entered" % (file_path, excluded_extension))
            _skipped()
            return True
    return False


def _check_file_owns_excluded_str(excluded_strings, file_path):
    for excluded_string in excluded_strings:
        if excluded_string in file_path:
            _warning(
                "the file %s is excluded regarding the excluded string %s you entered" % (file_path, excluded_string))
            _skipped()
            return True
    return False


def _check_able_open_file(file_path):
    try:
        open_test = open(file_path, 'r', encoding=ENCODING_INPUT_FILES)
        open_test.close()
        return True
    except FileNotFoundError:
        _error("the file " + CFILE_PATHS + "%s" % file_path + CBASE + " doesn't exist")
        _skipped()
        return False
    except PermissionError:
        _error("you don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CBASE)
        _skipped()
        return False
    except IsADirectoryError:
        _error("the path " + CFILE_PATHS + "%s" % file_path + CBASE + "is a directory, not a file")
        _skipped()
        return False
    except OSError:
        _error("no such device or address " + CFILE_PATHS + "%s" % file_path + CBASE)
        _skipped()
        return False


def _check_able_create_temporary(temporary_file_path, file_mask):
    try:
        open_test = open(temporary_file_path, 'w+')
        open_test.close()
        os.chmod(temporary_file_path, int(file_mask, 8))
        os.remove(temporary_file_path)
        return True
    except FileNotFoundError:
        _error("the file " + CFILE_PATHS + "%s" % temporary_file_path + CBASE + " doesn't exist")
        _skipped()
        return False
    except PermissionError:
        _error("you don't have the permission to create the file " + CFILE_PATHS + "%s" % temporary_file_path + CBASE)
        _skipped()
        return False
    except IsADirectoryError:
        _error(" the path " + CFILE_PATHS + "%s" % temporary_file_path + CBASE + "is a directory, not a file")
        _skipped()
        return False


def _check_binary_file(file_path):
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    try:
        if is_binary_string(open(file_path, 'rb').read(1024)):
            _warning("the file %s is a binary file" % file_path)
            _skipped()
            return True
        return False
    except PermissionError:
        _error("you don't have the permission to access the file " + CFILE_PATHS + "%s" % file_path + CBASE)
        _skipped()
        return True


def _check_symlink_path(file_path):
    if os.path.islink(file_path):
        _warning("the file %s is a symlink file" % file_path)
        _skipped()
        return True
    return False


def _get_temporary_file_path(file_path, excluded_paths):
    temporary_file_path = file_path + ".tmp"
    if os.path.exists(temporary_file_path):
        temporary_file_path = _find_tmp_file_not_existing(file_path)
    excluded_paths.append(temporary_file_path)
    return temporary_file_path


def _get_file_permission_mask(file_path):
    return oct(os.stat(file_path).st_mode & 0o777)


def _replace_local_recursive(directory_path, init_str, dest_str, black_list_extensions,
                             file_name_must_end_by, excluded_paths, excluded_strings, excluded_extensions, local,
                             nb_occs_found, nb_occs_replaced, ask_replace, case_sensitive, binary_accepted,
                             symlink_accepted):
    for directory_path, directory_names, file_names in os.walk(directory_path):
        for file_name in file_names:

            file_path = os.path.join(directory_path, file_name)

            if _check_file_owns_excluded_path(excluded_paths, file_path):
                continue

            if _check_file_owns_excluded_extension(excluded_extensions, file_path):
                continue

            if _check_file_owns_excluded_str(excluded_strings, file_path):
                continue

            if not _check_path_exists(file_path):
                _warning("the file path " + CFILE_PATHS + "%s" % file_path + CBASE +
                         " seems to cause problem, might be a broken symlink")
                continue

            _check_user_rights(file_path)
            if not _check_able_open_file(file_path):
                continue

            if black_list_extensions:
                if _check_file_extension_in_blacklist(file_path):
                    continue

            if not symlink_accepted:
                if _check_symlink_path(file_path):
                    continue

            if not binary_accepted:
                if _check_binary_file(file_path):
                    continue

            if file_name_must_end_by:
                if not _check_file_name_must_end_by(file_name_must_end_by, file_path):
                    continue

            file_mask = _get_file_permission_mask(file_path)

            temporary_file_path = _get_temporary_file_path(file_path, excluded_paths)
            if not _check_able_create_temporary(temporary_file_path, file_mask):
                continue

            if _check_init_str_in_file(file_path, init_str, case_sensitive):
                nb_occs_found, nb_occs_replaced = _file_replace(file_path, temporary_file_path,
                                                                init_str, dest_str,
                                                                nb_occs_found,
                                                                nb_occs_replaced,
                                                                ask_replace, case_sensitive, file_mask)
        if local:
            break
    return nb_occs_found, nb_occs_replaced


def _check_folder_path_exists(folder_path):
    if not os.path.isdir(folder_path):
        _warning(CFILE_PATHS + " %s " % folder_path + CBASE + "folder doesn't exist" +
                 "\n\tthe directory path to apply %s doesn't exist, you may review it" % folder_path)
        exit(1)


def _check_path_exists(path):
    if not os.path.exists(path):
        _warning(CFILE_PATHS + " %s " % path + CBASE + "path doesn't exist")
        return False
    return True


def _replace_specific(file_paths_to_apply, init_str, dest_str,
                      nb_occs_found, nb_occs_replaced, black_list_extensions, ask_replace, case_sensitive,
                      binary_accepted, symlink_accepted):
    for file_path in file_paths_to_apply:

        if not _check_path_exists(file_path):
            _warning("the file path %s seems to cause problem, might be a broken symlink" % file_path)
            _skipped()
            continue

        _check_user_rights(file_path)
        if not _check_able_open_file(file_path):
            continue

        if black_list_extensions:
            if _check_file_extension_in_blacklist(file_path):
                continue

        if not symlink_accepted:
            if _check_symlink_path(file_path):
                continue

        if not binary_accepted:
            if _check_binary_file(file_path):
                continue

        file_mask = _get_file_permission_mask(file_path)
        temporary_file_path = _get_temporary_file_path(file_path, [])
        if not _check_able_create_temporary(temporary_file_path, file_mask):
            continue

        if _check_init_str_in_file(file_path, init_str, case_sensitive):
            nb_occs_found, nb_occs_replaced = _file_replace(file_path, temporary_file_path, init_str,
                                                            dest_str, nb_occs_found,
                                                            nb_occs_replaced, ask_replace, case_sensitive, file_mask)
    return nb_occs_found, nb_occs_replaced


def _occs_summary(nb_occs_found, nb_occs_replaced, init_str):
    if nb_occs_found == 0:
        print(CFILE_PATHS + "\n\t0" + CBASE + " occurrence of " + COCCURRENCES + "%s" % init_str + CBASE + " found")
    elif nb_occs_found == 1:
        print(CFILE_PATHS + "\n\t1" + CBASE + " occurrence of " + COCCURRENCES + "%s" % init_str +
              CBASE + " found and " + CFILE_PATHS + "%s" % nb_occs_replaced + CBASE + " replaced")
    else:
        print(CFILE_PATHS + "\n\t%s" % nb_occs_found + CBASE + " occurrences of " + COCCURRENCES +
              "%s" % init_str + CBASE + " found and " + CFILE_PATHS + "%s" % nb_occs_replaced +
              CBASE + " replaced")


def _get_full_paths(dir_path_to_apply, file_paths_to_apply):
    if file_paths_to_apply:
        file_paths_list = []

        for file_name in file_paths_to_apply:
            file_paths_list.append(get_full_path_joined(file_name))

        file_paths_to_apply = file_paths_list

    if dir_path_to_apply is not None:
        dir_path_to_apply = get_full_path_joined(dir_path_to_apply)

    return dir_path_to_apply, file_paths_to_apply


def get_full_path_joined(given_path):
    return os.path.normpath((os.path.join(os.getcwd(), os.path.expanduser(given_path))))


def _check_integrity_of_mode_request(local, recursive, specific, dir_path_to_apply, file_paths_to_apply):
    if local or recursive:
        if file_paths_to_apply:
            _warning("the replace mode is not specific, file_paths_to_apply should be empty and "
                     "is: %s" % file_paths_to_apply + "\n\tfile_paths_to_apply should be empty")
            exit(1)
        if dir_path_to_apply is None:
            _warning("the replace mode is not specific, dir_path_to_apply should not be None" +
                     "\n\tdir_path_to_apply should be defined")
            exit(1)
        if not _check_path_exists(dir_path_to_apply):
            _error("the directory path %s doesn't exist" % dir_path_to_apply)
            exit(1)
        if not os.path.isdir(dir_path_to_apply):
            _info(CFILE_PATHS + "%s" + CBASE + " is a file, proceeding specific replace mode" % dir_path_to_apply)
            local = False
            recursive = False
            specific = True
            file_paths_to_apply.append(dir_path_to_apply)

    elif specific:
        if not file_paths_to_apply:
            _error("the replace mode is specific, file_paths_to_apply should not be empty and "
                   "is: %s" % file_paths_to_apply + "\n\tfile_paths_to_apply should not be empty in specific mode replacement")
            exit(1)
        if dir_path_to_apply is not None:
            _error("the replace mode is specific, dir_path_to_apply should be None" +
                   "\n\tdir_path_to_apply should not be defined")
            exit(1)

        file_paths = []
        for file_path in file_paths_to_apply:
            if not _check_path_exists(file_path):
                _warning(CFILE_PATHS + "%s" + CBASE + " doesn't exist, removing it from the file list" % file_path)
            elif os.path.isdir(file_path):
                _warning(CFILE_PATHS + "%s" + CBASE + " is a folder, removing it from the file list" % file_path)
            else:
                file_paths.append(file_path)

        file_paths_to_apply = file_paths
    return local, recursive, specific, dir_path_to_apply, file_paths_to_apply


def main():
    input_args = sys.argv[1:]
    _help_requested(input_args)
    _check_input_args(input_args)
    file_name_must_end_by, local, recursive, specific, ask_replace, case_sensitive, \
    black_list_extensions, binary_accepted, symlink_accepted, excluded_strings, \
    excluded_extensions, excluded_paths = _init_indicators()

    init_str, dest_str, dir_path_to_apply, file_paths_to_apply, \
    nb_occs_found, nb_occs_replaced = _init_args()

    file_name_must_end_by, init_str, dest_str, dir_path_to_apply, file_paths_to_apply, \
    local, recursive, specific, ask_replace, case_sensitive, black_list_extensions, binary_accepted, \
    symlink_accepted, excluded_strings, excluded_extensions, excluded_paths, args_not_used_indexes = \
        _treat_input_args(input_args, file_name_must_end_by, init_str, dest_str,
                          dir_path_to_apply, file_paths_to_apply, local, recursive, specific,
                          ask_replace, case_sensitive, black_list_extensions, binary_accepted, symlink_accepted,
                          excluded_strings, excluded_extensions, excluded_paths)

    _check_only_one_replace_mode_picked(local, specific, recursive)

    # finalize getting all the parameters
    if local or recursive:
        dir_path_to_apply, dest_str, init_str = \
            _get_final_args_local_recursive(dir_path_to_apply, dest_str,
                                            init_str, local, recursive, input_args,
                                            args_not_used_indexes)

    elif specific:
        file_paths_to_apply, dest_str, init_str = \
            _get_final_args_specific(file_paths_to_apply, dest_str,
                                     init_str, specific, input_args,
                                     args_not_used_indexes)
    else:
        _error("the replace mode can only be \"local\", \"recursive\" or \"specific\"" +
               "\n\tplease pick only one mode with the -l, -r or -s short options")
        exit(1)

    dir_path_to_apply, file_paths_to_apply = _get_full_paths(dir_path_to_apply, file_paths_to_apply)
    local, recursive, specific, dir_path_to_apply, file_paths_to_apply = _check_integrity_of_mode_request(
        local, recursive, specific, dir_path_to_apply, file_paths_to_apply)

    # apply the replace
    if local:
        nb_occs_found, nb_occs_replaced = \
            _replace_local_recursive(dir_path_to_apply, init_str, dest_str, black_list_extensions,
                                     file_name_must_end_by, excluded_paths, excluded_strings, excluded_extensions,
                                     local,
                                     nb_occs_found, nb_occs_replaced, ask_replace, case_sensitive,
                                     binary_accepted, symlink_accepted)

    elif recursive:
        nb_occs_found, nb_occs_replaced = \
            _replace_local_recursive(dir_path_to_apply, init_str, dest_str, black_list_extensions,
                                     file_name_must_end_by, excluded_paths, excluded_strings, excluded_extensions,
                                     local,
                                     nb_occs_found, nb_occs_replaced, ask_replace, case_sensitive,
                                     binary_accepted, symlink_accepted)

    elif specific:
        nb_occs_found, nb_occs_replaced = \
            _replace_specific(file_paths_to_apply, init_str, dest_str,
                              nb_occs_found, nb_occs_replaced, black_list_extensions, ask_replace,
                              case_sensitive, binary_accepted, symlink_accepted)
    else:
        _error("the replace mode can only be \"local\", \"recursive\" or \"specific\"\n\t"
               "please pick only one mode with the -l, -r or -s short options")
        exit(1)

    _occs_summary(nb_occs_found, nb_occs_replaced, init_str)


if __name__ == "__main__":
    main()
