import sublime, sublime_plugin 
from tab_utils import is_jumpy_tab


class JumpyCloser(sublime_plugin.EventListener):

	has_been_activated = False

	def on_activated(self, view):
		if not JumpyCloser.has_been_activated:
			if not is_jumpy_tab(view.name()) and not is_jumpy_tab(view.file_name()):
				JumpyCloser.has_been_activated = False

				for window in sublime.windows():
					for new_view in window.views():
						if is_jumpy_tab(new_view.name()) or is_jumpy_tab(new_view.file_name()):
							window.focus_view(view)
							window.focus_view(new_view)
							window.run_command('close')

		if is_jumpy_tab(view.name()) or is_jumpy_tab(view.file_name()):
			has_been_activated = True #reset
