import sublime, sublime_plugin
import string


class BaseJumpyCommand(sublime_plugin.TextCommand):

	settings = {}
	keys = []
	key_entered_thus_far = ''

	def __init__(self, edit):
		if not BaseJumpyCommand.settings:
			sublime_settings = sublime.load_settings('Jumpy.sublime-settings')

			jumpy_setting_names = ['jumpy_use_file_extensions', 'jumpy_use_upper_case_labels']
			for setting_name in jumpy_setting_names:
				try:
					retrieved_setting = sublime_settings.get(setting_name)
				except KeyError, e:
					pass

				BaseJumpyCommand.settings[setting_name] = retrieved_setting

		if not BaseJumpyCommand.keys:
			BaseJumpyCommand.keys = self.create_keys()

		sublime_plugin.TextCommand.__init__(self, edit)

	def set_jumpy_command_mode(self, new_view, on=True):
		new_view.settings().set('command_mode', not on)
		new_view.settings().set('jumpy_jump_mode', on)

	def create_keys(self):
		keys = []
		for c1 in string.lowercase:
			for c2 in string.lowercase:
				key = c1 + c2
				key = key.upper() if BaseJumpyCommand.settings['jumpy_use_upper_case_labels'] else key
				keys.append(key)
		return keys