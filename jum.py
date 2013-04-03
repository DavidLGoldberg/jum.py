import sublime
from settings import Settings
from async_utils import do_when
from base_jumpy import BaseJumpyCommand
from tab_utils import get_view_key, get_tab_name, TabCount
from index import IndexHandler


class JumpyCommand(BaseJumpyCommand):

	def activate_jumpy_mode(self):
		self._old_viewport = self.view.viewport_position()
		BaseJumpyCommand.old_offset = self.view.rowcol(self.view.layout_to_text(self._old_viewport))
		BaseJumpyCommand.old_file_size = self.view.substr(sublime.Region(0, self.view.size()))

		use_file_extensions = Settings.sublime_settings.get('jumpy_use_file_extensions')
		file_name = get_tab_name(self.view, \
			use_file_extensions if use_file_extensions else False)
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
		duplicate_contents(new_view, self.view.substr(self.view.visible_region()))

		regions = []
		view_key = get_view_key(self.view)
		if view_key:
			for (key, (row, col)) in IndexHandler.jump_locations[view_key].items():
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
			
			TabCount.count = 0
			self.activate_jumpy_mode()
