from os.path import basename

JUMPY_FILE_INDICATOR = '[Jumpy]'

class TabCount:
	count = 0

def get_view_key(view):
	view_key = ''
	if view.file_name():
		view_key = view.file_name()
	elif view.name():
		view_key = view.name()

	return view_key

def get_tab_name(view, use_file_extensions):
	if view.file_name() and use_file_extensions:
		file_name = JUMPY_FILE_INDICATOR + ' ' + basename(view.file_name())
	else:
		TabCount.count += 1
		file_name = JUMPY_FILE_INDICATOR + ' ' + str(TabCount.count)

	return file_name

def is_jumpy_tab (view):
	def _is_jumpy_tab (view_name):
		return basename(view_name).startswith(JUMPY_FILE_INDICATOR) if view_name is not None else False

	return _is_jumpy_tab(view.name()) or _is_jumpy_tab(view.file_name())
