import sublime
import re
from async_utils import do_when
from base_jumpy import BaseJumpyCommand
from tab_utils import get_tab_name


class JumpyCommand(BaseJumpyCommand):

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
		BaseJumpyCommand.old_offset = self.view.rowcol(self.view.layout_to_text(self._old_viewport))
		BaseJumpyCommand.old_file_size = self.view.substr(sublime.Region(0, self.view.size()))

		file_name = get_tab_name(self.view, BaseJumpyCommand.settings['jumpy_use_file_extensions'] \
			if 'jumpy_use_file_extensions' in BaseJumpyCommand.settings else False)
		label_view = self.view.window().open_file(file_name, sublime.TRANSIENT)

		do_when(lambda: not label_view.is_loading(), lambda: self.on_labels(), interval=10)

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
		duplicate_contents(new_view, self._visible_text)

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
			
			self._visible_text = self.view.substr(self.view.visible_region())
			locations = self.get_all_word_locations(self._visible_text)

			BaseJumpyCommand.jump_locations = self.get_jump_locations(BaseJumpyCommand.keys, locations)

			self.activate_jumpy_mode()
