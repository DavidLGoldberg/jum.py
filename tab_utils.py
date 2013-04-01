from os.path import basename

JUMPY_FILE_INDICATOR = '[Jumpy]'

def get_tab_name(view, use_file_extensions):
	file_name = JUMPY_FILE_INDICATOR
	if view.file_name() and use_file_extensions:
		file_name += ' ' + basename(view.file_name())

	return file_name

def is_jumpy_tab (name):
	return basename(name).startswith(JUMPY_FILE_INDICATOR) if name is not None else False