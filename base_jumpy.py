import sublime, sublime_plugin
from settings import Settings


class BaseJumpyCommand(sublime_plugin.TextCommand):

	keys = []
	key_entered_thus_far = ''

	def __init__(self, edit):
		Settings.load_settings()
		# It appeared that I needed the following code at one point.
		# I haven't been able to reproduce it though.  Leave it out for now.

		# for window in sublime.windows():
		# 	for view in window.views():
		# 		self.set_jumpy_command_mode(view, on=False)
		sublime_plugin.TextCommand.__init__(self, edit)

	def set_jumpy_command_mode(self, new_view, on=True):
		new_view.settings().set('command_mode', not on)
		new_view.settings().set('jumpy_jump_mode', on)
