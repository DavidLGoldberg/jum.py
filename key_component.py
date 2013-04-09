from base_jumpy import BaseJumpyCommand
from index import get_locations
from settings import Settings
import sublime_plugin, sublime


class JumpyCleanupCommand(BaseJumpyCommand):

	def run(self):
		view = self.window.active_view()

		view.set_read_only(False)

		view.run_command('undo')

		view.set_scratch(False)
		self.set_jumpy_command_mode(view, False)

class KeyComponentCommand(sublime_plugin.WindowCommand):
	def run(self, character):

		def cancel(window):
			print 'Jumpy: cancel'
			sublime.status_message('Jumpy: cancel')
			window.run_command('jumpy_cleanup')

		def jump(window):
			window.run_command('jumpy_cleanup')
			self.on_jump_entered()

		window = self.window
		if character in [' ', 'escape']:
			cancel(window)
		elif character == 'backspace':
			BaseJumpyCommand.key_entered_thus_far = ''
			sublime.status_message('Jumpy: *reset*')
		else:
			# TODO: += right?
			BaseJumpyCommand.key_entered_thus_far = \
				BaseJumpyCommand.key_entered_thus_far + character

			if len(BaseJumpyCommand.key_entered_thus_far) > 1: #Time to jump
				jump(window)
			else:
				sublime.status_message('Jumpy: %s' % BaseJumpyCommand.key_entered_thus_far)

	def on_jump_entered(self):
		try:
			(row, col), word = get_locations(self.window.active_view()) \
					[BaseJumpyCommand.key_entered_thus_far.upper() \
						if Settings.sublime_settings \
							.get('jumpy_use_upper_case_labels') \
						else BaseJumpyCommand.key_entered_thus_far]
		except KeyError, e:
			sublime.status_message('Jumpy: %s is not a jump point' % BaseJumpyCommand.key_entered_thus_far)
			return

		row += 1
		col += 1
		row_offset, col_offset = BaseJumpyCommand.old_offset
		self.window.run_command("goto_point", {"row": row + row_offset, "col": col + col_offset})

		print 'Jumpy: jumped to row: %s, col: %s, word: %s' % (row, col, word)
		sublime.status_message('Jumpy: jumped to row: %s, col: %s' % (row, col))
