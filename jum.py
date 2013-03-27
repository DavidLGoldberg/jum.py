import sublime, sublime_plugin
import GotoPoint
import tempfile
import string, re

def set_jumpy_commands(new_view, on=True):
	new_view.settings().set('command_mode', not on)
	new_view.settings().set('jumpy_jump_mode', on)

class JumpyCommand(sublime_plugin.WindowCommand):

	def create_keys(self):
		keys = []
		for c1 in string.lowercase:
			for c2 in string.lowercase:
				keys.append(c1 + c2)
		return keys

	def get_file_contents(self, view): #TODO add support for only pulling viewport
		region = sublime.Region(0, view.size())
		return view.substr(region)

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
		#This operation handles shortages of keys and or locations for a max of 26 x 26 = 676 keys.
		return dict(zip(keys, locations))

	def activate_jumpy_mode(self, old_view):
		self._old_viewport = old_view.viewport_position()

		global g_key_entered_thus_far
		g_key_entered_thus_far = ''

		self.window.open_file('Jumpy', sublime.TRANSIENT)

		sublime.set_timeout(self.on_labels, 25) #improve this later to check when ready.

	def on_labels(self):
		def duplicate_contents(new_view, file_contents):
			edit = new_view.begin_edit()
			new_view.insert(edit, new_view.size(), file_contents)
			new_view.end_edit(edit)	
		
		new_view = self.window.active_view()
		set_jumpy_commands(new_view)
		new_view.set_scratch(True)
		duplicate_contents(new_view, self._file_contents)
		new_view.set_viewport_position(self._old_viewport)

		global g_jump_locations
		regions = []
		for (key, (row, col)) in g_jump_locations.items():
			region_start = new_view.text_point(row, col)
			region_finish = new_view.text_point(row, col + 2)

			region = sublime.Region(region_start, region_finish)

			edit = new_view.begin_edit()
			new_view.replace(edit, region, key)
			new_view.end_edit(edit)

			regions.append(region)

		new_view.add_regions('jumpylabel', regions, 'jumpylabel')

	def run(self):
		view = self.window.active_view()
		if not view.settings().get('jumpy_jump_mode'): # don't open twice
			global g_jump_locations

			keys = self.create_keys()
			self._file_contents = self.get_file_contents(view)	
			locations = self.get_all_word_locations(self._file_contents)

			g_jump_locations = self.get_jump_locations(keys, locations)

			self.activate_jumpy_mode(view)

class InputKeyPart(sublime_plugin.TextCommand):
	def clean_up(self):
		set_jumpy_commands(self.view, False)
		shortcut_window = self.view.window()
		shortcut_window.run_command('close')

	def run(self, edit, character):

		def cancel(view):
			print 'Jumpy: cancel'
			sublime.status_message('Jumpy: cancel')
			self.clean_up()

		if character in [' ', 'escape']:
			cancel(self.view)
		else:
			global g_key_entered_thus_far
			g_key_entered_thus_far = g_key_entered_thus_far + character

			if len(g_key_entered_thus_far) > 1: #Time to jump
				self.jump(g_key_entered_thus_far)
			else:
				sublime.status_message('Jumpy: %s' % g_key_entered_thus_far)

	def jump(self, shortcut_entered):
		self.clean_up()
		sublime.set_timeout(self.on_jump_entered, 75)

	def on_jump_entered(self):
		original_view = sublime.active_window().active_view() # because shortcuts are closed

		row, col = g_jump_locations[g_key_entered_thus_far]
		row += 1
		col += 1
		original_view.run_command("goto_point", {"row": row , "col": col})
		
		print 'Jumpy: jumped to row: %s, col: %s' % (row, col)
		sublime.status_message('Jumpy: jumped to row: %s, col: %s' % (row, col))
