import sublime


class Settings():

	sublime_settings = None

	@staticmethod
	def load_settings():
		if not Settings.sublime_settings:
			Settings.sublime_settings = sublime.load_settings('Jumpy.sublime-settings')
