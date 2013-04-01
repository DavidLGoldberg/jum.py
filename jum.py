import sublime, sublime_plugin
import GotoPoint
import tempfile
import string, re
from os.path import basename
from async_utils import do_when

JUMPY_FILE_INDICATOR = '[Jumpy]'

class BaseJumpyCommand(sublime_plugin.TextCommand):

	settings = {}
	keys = []

	def __init__(self, edit):
		if not BaseJumpyCommand.settings:
			sublime_settings = sublime.load_settings('Jumpy.sublime-settings')

			jumpy_setting_names = ['jumpy_use_file_extensions', 'jumpy_use_upper_case_labels']
			for setting_name in jumpy_setting_names:
				try:
					retrieved_setting = sublime_settings.get(setting_name)
				except KeyError, e:
					pass

				BaseJumpyCommand.settings[setting_name] = retrieved_setting

		if not BaseJumpyCommand.keys:
			BaseJumpyCommand.keys = self.create_keys()

		sublime_plugin.TextCommand.__init__(self, edit)

	def get_tab_name(self, view):
		file_name = view.file_name()
		if file_name:
			if BaseJumpyCommand.settings['jumpy_use_file_extensions']:
				file_name = JUMPY_FILE_INDICATOR + ' ' + basename(file_name)
		else:
			file_name = JUMPY_FILE_INDICATOR
		return file_name

	def set_jumpy_command_mode(self, new_view, on=True):
		new_view.settings().set('command_mode', not on)
		new_view.settings().set('jumpy_jump_mode', on)

	def create_keys(self):
		keys = []
		for c1 in string.lowercase:
			for c2 in string.lowercase:
				key = c1 + c2
				key = key.upper() if BaseJumpyCommand.settings['jumpy_use_upper_case_labels'] else key
				keys.append(key)
		return keys

class JumpyCommand(BaseJumpyCommand):

	_visible_texts = {}

	def get_all_word_locations(self, dictionary_of_texts):
		locations = {}
		current_locations = []
		line_num = 0
		p = re.compile('[\w]{2,}') # TODO: "add something to handle 'quoted symbol characters'
		for key, text in dictionary_of_texts.items():
			for line in text.splitlines(False):
				for m in p.finditer(line):
					current_locations.append((line_num, m.start()))
				line_num += 1
			locations[key] = current_locations
		return locations

	def get_jump_locations(self, keys, locations):
		jump_locations = {}
		for key, value in locations:
			#This operation handles shortages of keys and or locations for a max of 26 x 26 = 676 keys.
			jump_locations[key] = dict(zip(keys, locations))
		return jump_locations

	def activate_jumpy_mode(self, view):
		self._old_viewport = view.viewport_position()
		BaseJumpyCommand.old_offset = view.rowcol(view.layout_to_text(self._old_viewport))
		BaseJumpyCommand.old_file_size = view.substr(sublime.Region(0, view.size()))

		file_name = self.get_tab_name(view)	
		current_window = view.window()
		if current_window:
			label_view = view.window().open_file(file_name, sublime.TRANSIENT)
			do_when(lambda: not label_view.is_loading(), lambda: self.on_labels(), interval=10)
			# I think I need to move do when out to run.. and maybe return back label view through to it..
			# because I need to block b4 starting the next for active_view below.. might not be so complicated though

	def on_labels(self):
		def duplicate_contents(new_view, visible_text):
			edit = new_view.begin_edit()
			padded_text = visible_text \
				.rjust(len(visible_text) + BaseJumpyCommand.old_offset[0], '\n')
			padded_text = padded_text \
				.ljust(len(padded_text) + \
					(BaseJumpyCommand.old_file_size.count('\n') - (padded_text.count('\n')) ), '\n')
			new_view.insert(edit, 0, padded_text)
			new_view.end_edit(edit)
		
		new_view = sublime.active_window().active_view()
		self.set_jumpy_command_mode(new_view)
		new_view.set_scratch(True)
		print self._visible_texts
		duplicate_contents(new_view, self._visible_texts[basename(new_view.file_name())])

		regions = []
		for (key, (row, col)) in BaseJumpyCommand.jump_locations.items():
			row += BaseJumpyCommand.old_offset[0]
			col += BaseJumpyCommand.old_offset[1]
			region_start = new_view.text_point(row, col)
			region_finish = new_view.text_point(row, col + 2)

			region = sublime.Region(region_start, region_finish)

			edit = new_view.begin_edit()
			new_view.replace(edit, region, key)
			new_view.end_edit(edit)

			regions.append(region)

		new_view.add_regions('jumpylabel', regions, 'jumpylabel')
		new_view.set_read_only(True)

		new_view.set_viewport_position(self._old_viewport, False)

	def run(self, edit):
		if not self.view.settings().get('jumpy_jump_mode'): # don't open twice
			BaseJumpyCommand.key_entered_thus_far = ''
			
			for window in sublime.windows():
				for view in window.views():
					self._visible_texts[self.get_tab_name(view)] = view.substr(view.visible_region())

			locations = self.get_all_word_locations(self._visible_texts)

			BaseJumpyCommand.jump_locations = self.get_jump_locations(BaseJumpyCommand.keys, locations)

			for window in sublime.windows():
				for view in window.views():
					self.activate_jumpy_mode(view)

class InputKeyPart(BaseJumpyCommand):
	def clean_up(self):
		self.set_jumpy_command_mode(self.view, False)
		shortcut_window = self.view.window()
		shortcut_window.run_command('close')

	def run(self, edit, character):

		def cancel(view):
			print 'Jumpy: cancel'
			sublime.status_message('Jumpy: cancel')
			self.clean_up()

		if character in [' ', 'escape']:
			cancel(self.view)
		elif character == 'backspace':
			BaseJumpyCommand.key_entered_thus_far = ''
			sublime.status_message('Jumpy: *reset*')
		else:
			BaseJumpyCommand.key_entered_thus_far = BaseJumpyCommand.key_entered_thus_far + character

			if len(BaseJumpyCommand.key_entered_thus_far) > 1: #Time to jump
				self.jump(BaseJumpyCommand.key_entered_thus_far)
			else:
				sublime.status_message('Jumpy: %s' % BaseJumpyCommand.key_entered_thus_far)

	def jump(self, shortcut_entered):
		self.clean_up()
		# I am pretty sure the code below is NOT needed.  That the run_command is in fact SYNCHRONOUS.
		#do_when(lambda: not self.view.name().startswith('Jumpy'), lambda: self.on_jump_entered(), 10)
		self.on_jump_entered()

	def on_jump_entered(self):
		original_view = sublime.active_window().active_view() # because shortcuts are closed

		try:
			row, col = BaseJumpyCommand \
				.jump_locations[BaseJumpyCommand.key_entered_thus_far.upper() \
					if BaseJumpyCommand.settings['jumpy_use_upper_case_labels'] \
					else BaseJumpyCommand.key_entered_thus_far]
		except KeyError, e:
			sublime.status_message('Jumpy: %s is not a jump point' % BaseJumpyCommand.key_entered_thus_far)
			return

		row += 1
		col += 1
		row_offset, col_offset = BaseJumpyCommand.old_offset
		original_view.run_command("goto_point", {"row": row + row_offset, "col": col + col_offset})

		print 'Jumpy: jumped to row: %s, col: %s' % (row, col)
		sublime.status_message('Jumpy: jumped to row: %s, col: %s' % (row, col))

class JumpyCloser(sublime_plugin.EventListener):

	has_been_activated = False

	def on_activated(self, view):
		is_jumpy_tab = lambda (string): basename(string).startswith(JUMPY_FILE_INDICATOR) if string is not None else False

		if not JumpyCloser.has_been_activated:
			if not is_jumpy_tab(view.name()) and not is_jumpy_tab(view.file_name()):
				JumpyCloser.has_been_activated = False

				for window in sublime.windows():
					for new_view in window.views():
						if is_jumpy_tab(new_view.name()) or is_jumpy_tab(new_view.file_name()):
							window.focus_view(view)
							window.focus_view(new_view)
							window.run_command('close')

		if is_jumpy_tab(view.name()) or is_jumpy_tab(view.file_name()):
			has_been_activated = True #reset
