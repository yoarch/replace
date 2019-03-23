#replacefs
Complete string replace tool on the all file system.

The replacefs tool permits to perform massive and controlled string replacements in files over the all file system in an intuitive and pleasant way. You will be able to replace a defined string to another recursively from a path, or locally in a defined path or in a list of files.

##installation
sudo pip3 install replacefs

#compatibility
python >= 3

##usage
**python replace.py** [-h] [-l] [-r] [-s] [-a] [-c]
                  [--initial_string INITIAL_STRING]
                  [--destination_string DESTINATION_STRING]
                  [--directory_path FOLDER_PATH]
                  [--file_paths_list FILE_PATH_01 FILE_PATH_02 ...]
                  [--filename_must_end_by END_STRING_01 END_STRING_02 ...]
                  [--no_ask_confirmation] [--case_insensitive]
                  [--extension_filter] [--all_extensions]
                  [--add_excluded_extensions END_STRING_01 END_STRING_02 ...]
                  [--add_excluded_strings STRING_01 STRING_02 ...]
                  [--excluded_paths EXCLUDED_PATH_01 EXCLUDED_PATH_01 ...]
                  [--binary_exclusion] [--binary_accepted]
                  [--symlink_exclusion] [--symlink_accepted]

options:
  **-h, --help**        show this help message and exit
  **-l**        perform local replacement in FOLDER_PATH. Enabled by default
  **-r**        perform recursive replacement from FOLDER_PATH
  **-s**        perform specific replacement on FILE_PATH_01 FILE_PATH_02 given by --list_files_paths_to_apply
  **-a, --ask_confirmation, --ask**        ask for confirmation to perform replacement at any INITIAL_STRING occurrence. Enabled by default
  **-c, --case_sensitive, --case_respect**        respect case when searching for occurrences. Enabled by default
  **--initial_string, --initial, --init INITIAL_STRING**        precise the string to search and replace
  **--destination_string, --destination, --dest DESTINATION_STRING**        precise the string to replace the INITIAL_STRING strings found
  **--directory_path, --dirpath, --path FOLDER_PATH**        precise the path of the directory to perform the replacement from
  **--file_paths_list, --file_paths FILE_PATH_01 FILE_PATH_02 ...**        precise the list of file paths to perform the replacement on
  **--filename_must_end_by, --end_by END_STRING_01 END_STRING_02 ...**        precise the list of acceptable end string to filter the files regarding their end names
  **--no_ask_confirmation, --no_ask**        enable no asking mode. Perform replacement without asking confirmation
  **--case_insensitive, --no_case_respect**        enable case insensitive. Search for INITIAL_STRING string in insensitive case mode
  **--extension_filter, --no_all_extensions**        enable blacklist extension filter. The blacklist extension owns more than 60 audio, image and video extensions such as "mp3", "jpg" or "mp4". This mode is enabled by default
  **--all_extensions, --no_extension_filter**        disable blacklist extension filter.
  **--add_excluded_extensions, --filter_extensions END_STRING_01 END_STRING_02 ...**        precise the unacceptable end strings to filter the files regarding their end names
  **--add_excluded_strings, --filter_strings STRING_01 STRING_02 ...**        precise the unacceptable strings to filter the files regarding their names
  **--excluded_paths EXCLUDED_PATH_01 EXCLUDED_PATH_01**        precise the paths to exclude when searching for the INITIAL_STRING in the file system
  **--binary_exclusion, --no_binary**        refuse binary files. Enabled by default
  **--binary_accepted, --no_binary_exclusion, --binary**        accept binary files
  **--symlink_accepted, --no_symlink_exclusion, --symlink**        refuse symlinks. Enabled by default
  **--symlink_exclusion, --no_symlink**        accept symlinks


## examples
for help:
replace --help
python replace.py -h

local replace "titi" occurrences to "toto" in current directory:
replace -l titi toto .

recursive replace from the child directory "test":
replace -r titi toto test

specific replace in the files "test01" "test/test02":
replace -s titi toto test01 test/test02

# black list extensions
all the extensions by default in the blacklist:
"mp3", "MP3", "wav", "WAV", "m4a", "M4A", "aac", "AAC", "mp1", "MP1", "mp2", "MP2", "mpg", "MPG", "flac", "FLAC", "jpg", "JPG", "jpeg", "JPEG", "png", "PNG", "tif", "TIF", "gif", "GIF", "bmp", "BMP", "pjpeg", "PJPEG", "mp4", "MP4", "mpeg", "MPEG", "avi", "AVI", "wma", "WMA", "ogg", "OGG", "quicktime", "QUICKTIME", "webm", "WEBM", "mp2t", "MP2T", "flv", "FLV", "mov", "MOV", "webm", "WEBM", "mkv", "MKV", "class", "CLASS"

use   *--all_extensions* or *--no_extension_filter* to disable blacklist extension filter.
use   *--add_excluded_extensions* or *--filter_extensions* to add some more

## suggestions
some useful functions:
```
function rp {
#ex:  rp titi toto

	nb_param="$#"

	if [ "$nb_param" -lt 2 ]; then
		echo -e "\n\t$WARNING needs at least 2 strings arguments such as:\n\t\treplace titi toto"
	elif [ "$nb_param" -eq 2 ]; then
		replace -l "$@" .
	elif [ "$nb_param" -eq 3 ]; then
		replace -l "$@"
	elif [ "$nb_param" -gt 3 ]; then
		echo -e "$WARNING specific mode replace"
		replace -s "$@"
	fi
}

function rplocal { rp $@; }

function rprecursive {
#ex:  rprecursive titi toto

	nb_param="$#"

	if [ "$nb_param" -lt 2 ]; then
		echo -e "\n\t$WARNING needs at least 2 strings arguments such as:\n\t\treplace titi toto"
	elif [ "$nb_param" -eq 2 ]; then
		replace -r "$@" .
	elif [ "$nb_param" -eq 3 ]; then
		replace -r "$@"
	else
		echo -e "\n\t$WARNING at  most 3 arguments ..."
	fi
}

function rpcaseinsensitive {
#ex:  rpcaseinsensitive titi toto

	nb_param="$#"

	if [ "$nb_param" -lt 2 ]; then
		echo -e "\n\t$WARNING needs at least 2 strings arguments such as:\n\t\treplace titi toto"
	elif [ "$nb_param" -eq 2 ]; then
		replace --case_insensitive -l "$@" .
	elif [ "$nb_param" -eq 3 ]; then
		replace --case_insensitive -l "$@"
	elif [ "$nb_param" -gt 3 ]; then
		echo -e "$WARNING specific mode replace"
		replace --case_insensitive -s "$@"
	fi
}

function rpcaseinsensitivelocal { rpcaseinsensitive $@ ; }

function rprecursivecaseinsensitive {
	#ex:  rprecursivecaseinsensitive titi toto

		nb_param="$#"

		if [ "$nb_param" -lt 2 ]; then
			echo -e "\n\t$WARNING needs at least 2 strings arguments such as:\n\t\treplace titi toto"
		elif [ "$nb_param" -eq 2 ]; then
			replace --case_insensitive -r "$@" .
		elif [ "$nb_param" -eq 3 ]; then
			replace --case_insensitive -r "$@"
		else
			echo -e "\n\t$WARNING at  most 3 arguments ..."
		fi
}
```
