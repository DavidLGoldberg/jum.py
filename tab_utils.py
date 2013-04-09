from os.path import basename

JUMPY_FILE_INDICATOR = '[Jumpy'

class TabCount:
	count = 0

def get_view_key(view):
	return view.id()

def get_tab_name(view, use_file_extensions):
	TabCount.count += 1
	tab_name = JUMPY_FILE_INDICATOR + ' ' + str(TabCount.count) + ']'

	if view.file_name() and use_file_extensions:
		tab_name += ' ' + basename(view.file_name())

	return tab_name

def is_jumpy_tab (view):
	def _is_jumpy_tab (view_name):
		return basename(view_name).startswith(JUMPY_FILE_INDICATOR) if view_name is not None else False

	return _is_jumpy_tab(view.file_name()) or _is_jumpy_tab(view.name())
