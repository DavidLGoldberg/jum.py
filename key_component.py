import sublime
from base_jumpy import BaseJumpyCommand


class KeyComponentCommand(BaseJumpyCommand):
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

