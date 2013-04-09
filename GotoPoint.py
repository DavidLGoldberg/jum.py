import sublime, sublime_plugin

class GotoPointCommand(sublime_plugin.TextCommand):

	def run(self, edit, row, col):
		view = self.view

		# Convert from 1 based to a 0 based line number
		row = int(row) - 1
		col = int(col) - 1

		pt = view.text_point(row, col)
		
		view.sel().clear()
		view.sel().add(sublime.Region(pt))

		view.show(pt, False)

