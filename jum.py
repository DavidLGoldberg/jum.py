import sublime
from settings import Settings
from base_jumpy import BaseJumpyCommand
from index import get_locations


class JumpyCommand(BaseJumpyCommand):

	def activate_jumpy_mode(self):
		view = self.window.active_view()

		BaseJumpyCommand.old_offset = view.rowcol(view.layout_to_text(view.viewport_position()))

		self.set_jumpy_command_mode(view) # must occur before edits for indexing rules
		view.set_scratch(True) # prevents buffer marked as dirty

		regions = []

		edit = view.begin_edit()
		
		for (key, ((row, col), word)) in get_locations(view).items():
			row += BaseJumpyCommand.old_offset[0]
			col += BaseJumpyCommand.old_offset[1]
			region_start = view.text_point(row, col)
			region_finish = view.text_point(row, col + 2)

			region = sublime.Region(region_start, region_finish)

			view.replace(edit, region, key)

			regions.append(region)

		view.end_edit(edit)

		view.add_regions('jumpylabel', regions, 'jumpylabel')

		view.set_read_only(True) # Disable all non jumpy edits

	def run(self):
		view = self.window.active_view()
		if not view.settings().get('jumpy_jump_mode'): # don't open twice
			BaseJumpyCommand.key_entered_thus_far = ''
			
			self.activate_jumpy_mode()
