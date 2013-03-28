import sublime, sublime_plugin

class GotoPointCommand(sublime_plugin.TextCommand):

	def run(self, edit, row, col):
		# Convert from 1 based to a 0 based line number
		row = int(row) - 1
		col = int(col) - 1

		pt = self.view.text_point(row, col)

		self.view.sel().clear()
		self.view.sel().add(sublime.Region(pt))

		self.view.show(pt, False)
