from settings import Settings
from tab_utils import is_jumpy_tab, get_view_key
import sublime, sublime_plugin
import string, re

class IndexHandler(sublime_plugin.EventListener):

	keys = []
	jump_locations = {}

	def __init__(self):
		Settings.load_settings()
		IndexHandler.keys = self.create_keys()

	def create_keys(self):
		keys = []
		for c1 in string.lowercase:
			for c2 in string.lowercase:
				key = c1 + c2
				key = key.upper() if Settings.sublime_settings.get('jumpy_use_upper_case_labels') else key
				keys.append(key)
		return keys

	def on_activated(self, view):
		if not is_jumpy_tab(view):
			self.store_locations(view)

	def on_modified(self, view):
		if not is_jumpy_tab(view):
			self.store_locations(view)

	def on_close(self, view):
		view_key = get_view_key(view) 
		if view_key in self.jump_locations: del self.jump_locations[view_key]

	def store_locations(self, view):
		visible_text = view.substr(view.visible_region())
		locations = self.get_all_word_locations(visible_text)

		view_key = get_view_key(view)

		if view_key:
			IndexHandler.jump_locations[view_key] = \
				self.get_jump_locations(IndexHandler.keys, locations)

	def get_all_word_locations(self, file_contents):
		locations = []
		line_num = 0
		p = re.compile('[\w]{2,}') # TODO: "add something to handle 'quoted symbol characters'
		for line in file_contents.splitlines(False):
			for m in p.finditer(line):
				locations.append((line_num, m.start()))
			line_num += 1
		return locations

	def get_jump_locations(self, keys, locations):
		# This operation handles shortages of keys and or locations for a max of 26 x 26 = 676 keys.
		return dict(zip(keys, locations))

