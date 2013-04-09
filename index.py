from settings import Settings
import string, re

def create_keys():
	Settings.load_settings() # TODO: this will be saved?
	keys = []
	for c1 in string.lowercase:
		for c2 in string.lowercase:
			key = c1 + c2
			key = key.upper() if Settings.sublime_settings \
				.get('jumpy_use_upper_case_labels') else key
			keys.append(key)
	return keys

_keys = create_keys()

def get_locations(view):
	visible_text = view.substr(view.visible_region())
	info = _get_all_word_info(visible_text)

	return _get_jump_info(_keys, info)

def _get_all_word_info(file_contents):
	info = []
	line_num = 0
	pattern = re.compile('([\w]){2,}') # TODO: "add something to handle 'quoted symbol characters'
	for line in file_contents.splitlines(False):
		for match in pattern.finditer(line):
			info.append(((line_num, match.start()), match.group(0)))
		line_num += 1
	return info

def _get_jump_info(keys, info):
	# This operation handles shortages of keys and or locations for a max of 26 x 26 = 676 keys.
	return dict(zip(keys, info))
