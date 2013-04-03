import sublime, sublime_plugin
from settings import Settings


class BaseJumpyCommand(sublime_plugin.TextCommand):

	keys = []
	key_entered_thus_far = ''

	def __init__(self, edit):
		Settings.load_settings()
		sublime_plugin.TextCommand.__init__(self, edit)

	def set_jumpy_command_mode(self, new_view, on=True):
		new_view.settings().set('command_mode', not on)
		new_view.settings().set('jumpy_jump_mode', on)
