import sublime, sublime_plugin
from settings import Settings


class BaseJumpyCommand(sublime_plugin.WindowCommand):

	keys = []
	key_entered_thus_far = ''

	def __init__(self, window):
		Settings.load_settings()
		for view in window.views():
			self.set_jumpy_command_mode(view, on=False)
		sublime_plugin.WindowCommand.__init__(self, window)

	def set_jumpy_command_mode(self, new_view, on=True):
		new_view.settings().set('command_mode', not on)
		new_view.settings().set('jumpy_jump_mode', on)
