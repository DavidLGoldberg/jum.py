import sublime, sublime_plugin 
from tab_utils import is_jumpy_tab


class JumpyCloser(sublime_plugin.EventListener):

	has_been_activated = False

	def on_activated(self, view):
		if not JumpyCloser.has_been_activated:
			if not is_jumpy_tab(view):
				JumpyCloser.has_been_activated = False

				for window in sublime.windows():
					for new_view in window.views():
						if is_jumpy_tab(new_view) or is_jumpy_tab(new_view):
							window.focus_view(view)
							window.focus_view(new_view)
							window.run_command('close')

		if is_jumpy_tab(view):
			has_been_activated = True #reset
