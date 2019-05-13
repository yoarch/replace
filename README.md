# replacefs
Search and replace tool for strings on the all system.

The replacefs tool permits to perform massive and controlled string replacements in files over the all file system in an intuitive and pleasant way. You will be able to replace a defined string to another recursively from a path, or locally in a defined path or in a list of files.

# installation
```sh
with pip:
sudo pip3 install replacefs

with yay:
yay -a replace

with yaourt:
yaourt -a replace
```

# compatibility
python >= 3

# usage
<pre>
<b>replacefs</b> [-h] [-l] [-r] [-s] [-a] [-c]
        [--initial_string <b>INITIAL_STRING</b>]
        [--destination_string <b>DESTINATION_STRING</b>]
        [--directory_path <b>FOLDER_PATH</b>]
        [--file_paths_list <b>FILE_PATH_01 FILE_PATH_02 ...</b>]
        [--filename_must_end_by <b>END_STRING_01 END_STRING_02 ...</b>]
        [--no_ask_confirmation] [--case_insensitive ]
        [--extension_filter] [--all_extensions]
        [--add_excluded_extensions <b>END_STRING_01 END_STRING_02 ...</b>]
        [--add_excluded_strings <b>STRING_01 STRING_02 ...</b>]
        [--excluded_paths <b>EXCLUDED_PATH_01 EXCLUDED_PATH_01 ...</b>]
        [--binary_exclusion] [--binary_accepted]
        [--symlink_exclusion] [--symlink_accepted] [--end_param]
<b>options:</b>
<!-- -->        <b>-h, --help</b>        show this help message and exit
<!-- -->        <b>-l</b>        perform local replacement in <b>FOLDER_PATH</b>. Enabled by default
<!-- -->        <b>-r</b>        perform recursive replacement from <b>FOLDER_PATH</b>
<!-- -->        <b>-s</b>        perform specific replacement on <b>FILE_PATH_01 FILE_PATH_02</b> given by --list_files_paths_to_apply
<!-- -->        <b>-a, --ask_confirmation, --ask</b>        ask for confirmation to perform replacement at any <b>INITIAL_STRING</b> occurrence. Enabled by default
<!-- -->        <b>-c, --case_sensitive, --case_respect</b>        respect case when searching for occurrences. Enabled by default
<!-- -->        <b>--initial_string, --initial, --init INITIAL_STRING</b>        precise the string to search and replace
<!-- -->        <b>--destination_string, --destination, --dest DESTINATION_STRING</b>        precise the string to replace the <b>INITIAL_STRING</b> strings found
<!-- -->        <b>--directory_path, --dirpath, --path FOLDER_PATH</b>        precise the path of the directory to perform the replacement from
<!-- -->        <b>--file_paths_list, --file_paths FILE_PATH_01 FILE_PATH_02 ...</b>        precise the list of file paths to perform the replacement on
<!-- -->        <b>--filename_must_end_by, --end_by END_STRING_01 END_STRING_02 ...</b>        precise the list of acceptable end string to filter the files regarding their end names
<!-- -->        <b>--no_ask_confirmation, --no_ask</b>        enable no asking mode. Perform replacement without asking confirmation
<!-- -->        <b>--case_insensitive, --no_case_respect</b>        enable case insensitive. Search for <b>INITIAL_STRING</b> string in insensitive case mode
<!-- -->        <b>--extension_filter, --no_all_extensions</b>        enable blacklist extension filter. The blacklist extension owns more than 60 audio, image and video extensions such as "mp3", "jpg" or "mp4". This mode is enabled by default
<!-- -->        <b>--all_extensions, --no_extension_filter</b>        disable blacklist extension filter.
<!-- -->        <b>--add_excluded_extensions, --filter_extensions END_STRING_01 END_STRING_02 ...</b>        precise the unacceptable end strings to filter the files regarding their end names
<!-- -->        <b>--add_excluded_strings, --filter_strings STRING_01 STRING_02 ...</b>        precise the unacceptable strings to filter the files regarding their names
<!-- -->        <b>--excluded_paths EXCLUDED_PATH_01 EXCLUDED_PATH_01</b>        precise the paths to exclude when searching for the <b>INITIAL_STRING</b> in the file system
<!-- -->        <b>--binary_exclusion, --no_binary</b>        refuse binary files. Enabled by default
<!-- -->        <b>--binary_accepted, --no_binary_exclusion, --binary</b>        accept binary files
<!-- -->        <b>--symlink_accepted, --no_symlink_exclusion, --symlink</b>        refuse symlinks. Enabled by default
<!-- -->        <b>--symlink_exclusion, --no_symlink</b>        accept symlinks
<!-- -->        <b>-end_param, --end</b>        precise the end of a parameter enumeration
</pre>


# examples
for help:<br/>
```sh
rp -h
or
replacefs --help
```

**local** replace "titi" occurrences to "toto" in current directory:<br/>
```sh
rp -l titi toto .
```

**recursive** replace from the child directory "test":<br/>
```sh
replacefs -r titi toto test
```
**specific** replace in the files "test01" "test/test02":<br/>
```sh
replacefs -s titi toto test01 test/test02
```

# black list extensions
all the extensions by default in the blacklist:<br/>
**"mp3", "MP3", "wav", "WAV", "m4a", "M4A", "aac", "AAC", "mp1", "MP1", "mp2", "MP2", "mpg", "MPG", "flac", "FLAC", "jpg", "JPG", "jpeg", "JPEG", "png", "PNG", "tif", "TIF", "gif", "GIF", "bmp", "BMP", "pjpeg", "PJPEG", "mp4", "MP4", "mpeg", "MPEG", "avi", "AVI", "wma", "WMA", "ogg", "OGG", "quicktime", "QUICKTIME", "webm", "WEBM", "mp2t", "MP2T", "flv", "FLV", "mov", "MOV", "webm", "WEBM", "mkv", "MKV", "class", "CLASS"**

use   ***--all_extensions*** or ***--no_extension_filter*** to disable blacklist extension filter.
use   ***--add_excluded_extensions*** or ***--filter_extensions*** to add some more

# suggestions
some useful bash functions with replace:<br/>
```sh
function replace {
#ex:  replace titi toto

	nb_param="$#"

	if [ "$nb_param" -lt 2 ]; then
		echo -e "\n\t$WARNING needs at least 2 strings arguments such as:\n\t\treplace titi toto"
	elif [ "$nb_param" -eq 2 ]; then
		rp -l "$@" .
	elif [ "$nb_param" -eq 3 ]; then
		rp -l "$@"
	elif [ "$nb_param" -gt 3 ]; then
		echo -e "$WARNING specific mode replace"
		rp -s "$@"
	fi
}

function rplocal { replace $@; }

function rprecursive {
#ex:  rprecursive titi toto

	nb_param="$#"

	if [ "$nb_param" -lt 2 ]; then
		echo -e "\n\t$WARNING needs at least 2 strings arguments such as:\n\t\treplace titi toto"
	elif [ "$nb_param" -eq 2 ]; then
		rp -r "$@" .
	elif [ "$nb_param" -eq 3 ]; then
		rp -r "$@"
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
		rp --case_insensitive -l "$@" .
	elif [ "$nb_param" -eq 3 ]; then
		rp --case_insensitive -l "$@"
	elif [ "$nb_param" -gt 3 ]; then
		echo -e "$WARNING specific mode replace"
		rp --case_insensitive -s "$@"
	fi
}

function rpcaseinsensitivelocal { rpcaseinsensitive $@ ; }

function rprecursivecaseinsensitive {
	#ex:  rprecursivecaseinsensitive titi toto

		nb_param="$#"

		if [ "$nb_param" -lt 2 ]; then
			echo -e "\n\t$WARNING needs at least 2 strings arguments such as:\n\t\treplace titi toto"
		elif [ "$nb_param" -eq 2 ]; then
			rp --case_insensitive -r "$@" .
		elif [ "$nb_param" -eq 3 ]; then
			rp --case_insensitive -r "$@"
		else
			echo -e "\n\t$WARNING at  most 3 arguments ..."
		fi
}
```
