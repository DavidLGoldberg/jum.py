import sublime_plugin, sublime
from settings import Settings
from index import Indexer


class BaseJumpyCommand(sublime_plugin.WindowCommand):

	key_entered_thus_far = ''
	indexer = Indexer()

	def __init__(self, window):
		Settings.load_settings()
		for window in sublime.windows():
			for view in window.views():
				view.settings().set('jumpy_jump_mode', False)
		sublime_plugin.WindowCommand.__init__(self, window)

	def set_jumpy_command_mode(self, view):
		settings = view.settings()

		settings.set('command_mode', False)
		settings.set('jumpy_jump_mode', True)

	def restore_command_modes(self, view):
		settings = view.settings()

		view.run_command('exit_insert_mode')
		settings.set('jumpy_jump_mode', False)
