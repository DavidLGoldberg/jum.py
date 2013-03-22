import sublime, sublime_plugin
import GotoPoint
import tempfile
import string, re

class JumpyCommand(sublime_plugin.WindowCommand):

	def create_keys(self):
		keys = []
		for c1 in string.lowercase:
		    for c2 in string.lowercase:
		        keys.append(c1 + c2)
		return keys

	def get_file_contents(self, view):
		region = sublime.Region(0, view.size())
		return view.substr(region)

	def get_all_word_locations(self, file_contents):
		locations = []
		line_num = 0
		p = re.compile('[\w]{2,}')
		for line in file_contents.splitlines(False):
			for m in p.finditer(line):
				locations.append((line_num, m.start()))
			line_num += 1
		return locations

	def get_jump_locations(self, keys, locations):
		#This operation handles shortages of keys and or locations for a max of 26 x 26 = 676 keys.
		return dict(zip(keys, locations))

	def get_current_pos(self, view):
		return view.rowcol(view.sel()[0].begin())

	def show_jump_locations(self, old_view):
		self._old_viewport = old_view.viewport_position()

		self.window.open_file('Jumpy', sublime.TRANSIENT)

		sublime.set_timeout(self.on_labels, 25) #improve this later to check when ready.

	def on_labels(self):
		new_view = self.window.active_view()
		new_view.set_scratch(True)

		edit = new_view.begin_edit()
		new_view.insert(edit, new_view.size(), self._file_contents)
		new_view.end_edit(edit)

		new_view.set_viewport_position(self._old_viewport)

		regions = []
		for (key, (row, col)) in self._jump_locations.items():
			region_start = new_view.text_point(row, col)
			region_finish = new_view.text_point(row, col + 2)

			region = sublime.Region(region_start, region_finish)

			edit = new_view.begin_edit()
			new_view.replace(edit, region, key)
			new_view.end_edit(edit)

			regions.append(region)

		new_view.add_regions('jumpylabel', regions, 'jumpylabel')

	def run(self):
		keys = self.create_keys()
		view = self.window.active_view()
		self._file_contents = self.get_file_contents(view)	
		locations = self.get_all_word_locations(self._file_contents)

		self._jump_locations = self.get_jump_locations(keys, locations)
		self._current_pos = self.get_current_pos(view)

		self.show_jump_locations(view)

		self.window.show_input_panel("Jumpy to ?", "", self.on_key_entered, None, None)

	def on_key_entered(self, key):
		self._key_entered = key	
		self.window.run_command('close')			

		original_view = self.window.active_view()

		row, col = self._jump_locations[self._key_entered]
		original_view.run_command("goto_point", {"row": row + 1, "col": col + 1})
		print 'jumpy jumped to row: %s, col: %s' % (row, col)
		sublime.status_message('jumpy jumped to row: %s, col: %s' % (row, col))
