import sublime, sublime_plugin
import GotoPoint
import tempfile
import string, re
from os.path import basename

class BaseJumpyCommand(sublime_plugin.TextCommand):

	key_entered_thus_far = ''
	jump_locations = {}

	def set_jumpy_commands(self, new_view, on=True):
		new_view.settings().set('command_mode', not on)
		new_view.settings().set('jumpy_jump_mode', on)

class JumpyCommand(BaseJumpyCommand):

	def create_keys(self):
		keys = []
		for c1 in string.lowercase:
			for c2 in string.lowercase:
				keys.append(c1 + c2)
		return keys

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

	def activate_jumpy_mode(self):
		self._old_viewport = self.view.viewport_position()
		BaseJumpyCommand.old_offsets = self.view.rowcol(self.view.layout_to_text(self._old_viewport))

		file_name = 'Jumpy_' + basename(self.view.file_name()) if sublime.load_settings('Jumpy.sublime-settings').get('use_file_extensions') else 'Jumpy'
		self.view.window().open_file(file_name, sublime.TRANSIENT)

		sublime.set_timeout(self.on_labels, 25) #improve this later to check when ready.

	def on_labels(self):
		def duplicate_contents(new_view, file_contents):
			edit = new_view.begin_edit()
			padded_file_contents = file_contents.rjust(len(file_contents) + BaseJumpyCommand.old_offsets[0], '\n')
			new_view.insert(edit, 0, padded_file_contents)
			new_view.end_edit(edit)	
		
		new_view = sublime.active_window().active_view()
		self.set_jumpy_commands(new_view)
		new_view.set_scratch(True)
		duplicate_contents(new_view, self._visible_text)

		regions = []
		for (key, (row, col)) in BaseJumpyCommand.jump_locations.items():
			row += BaseJumpyCommand.old_offsets[0]
			col += BaseJumpyCommand.old_offsets[1]
			region_start = new_view.text_point(row, col)
			region_finish = new_view.text_point(row, col + 2)

			region = sublime.Region(region_start, region_finish)

			edit = new_view.begin_edit()
			new_view.replace(edit, region, key)
			new_view.end_edit(edit)

			regions.append(region)

		new_view.add_regions('jumpylabel', regions, 'jumpylabel')

		new_view.set_viewport_position(self._old_viewport)

	def run(self, edit):
		if not self.view.settings().get('jumpy_jump_mode'): # don't open twice
			BaseJumpyCommand.key_entered_thus_far = ''
			
			keys = self.create_keys()

			self._visible_text = self.view.substr(self.view.visible_region())
			locations = self.get_all_word_locations(self._visible_text)

			BaseJumpyCommand.jump_locations = self.get_jump_locations(keys, locations)

			self.activate_jumpy_mode()

class InputKeyPart(BaseJumpyCommand):
	def clean_up(self):
		self.set_jumpy_commands(self.view, False)
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
			BaseJumpyCommand.key_entered_thus_far = BaseJumpyCommand.key_entered_thus_far + character

			if len(BaseJumpyCommand.key_entered_thus_far) > 1: #Time to jump
				self.jump(BaseJumpyCommand.key_entered_thus_far)
			else:
				sublime.status_message('Jumpy: %s' % BaseJumpyCommand.key_entered_thus_far)

	def jump(self, shortcut_entered):
		self.clean_up()
		sublime.set_timeout(self.on_jump_entered, 25)

	def on_jump_entered(self):
		original_view = sublime.active_window().active_view() # because shortcuts are closed

		row, col = BaseJumpyCommand.jump_locations[BaseJumpyCommand.key_entered_thus_far]
		row += 1
		col += 1

		row_offset, col_offset = BaseJumpyCommand.old_offsets
		original_view.run_command("goto_point", {"row": row + row_offset, "col": col + col_offset})

		print 'Jumpy: jumped to row: %s, col: %s' % (row, col)
		sublime.status_message('Jumpy: jumped to row: %s, col: %s' % (row, col))
