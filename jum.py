import sublime
from settings import Settings
from base_jumpy import BaseJumpyCommand


class JumpyCommand(BaseJumpyCommand):

	def activate_jumpy_mode(self, view):
		BaseJumpyCommand.old_offset = view.rowcol(view.layout_to_text(view.viewport_position()))

		self.set_jumpy_command_mode(view) # must occur before edits for indexing rules
		view.set_scratch(True) # prevents buffer marked as dirty

		regions = []

		edit = view.begin_edit()
		
		current_views_labels = BaseJumpyCommand.indexer.all_labels[view]
		for (key, ((row, col), word)) in current_views_labels:
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
		windows = sublime.windows()
		all_views = []

		for window in windows:
			# don't open twice:
			if window.active_view().settings().get('jumpy_jump_mode'):
				return

			all_views += window.views()

		print 'Jumpy: jump mode'
		BaseJumpyCommand.key_entered_thus_far = ''
		BaseJumpyCommand.indexer.create_index(all_views)
		for view in all_views:
			self.activate_jumpy_mode(view)
