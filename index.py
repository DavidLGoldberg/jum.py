from settings import Settings
import itertools
import string, re

def create_keys():
    Settings.load_settings() # TODO: this will be saved?
    use_upper = Settings.sublime_settings.get("jumpy_use_upper_case_labels")
    base = string.uppercase if use_upper else string.lowercase
    keys = [''.join(pair) for pair in itertools.permutations(base, 2)]
    return keys

_keys = create_keys()

class Indexer:

	def __init__(self):
		self._all_labels = {}
		self._all_jumps = {} 

	def create_index(self, views):
		keys = iter(_keys)
		for view in views:
			self.all_labels[view] = []
			visible_text = view.substr(view.visible_region())
			line_num = 0
			pattern = re.compile('([\w]){2,}') # TODO: "add something to handle 'quoted symbol characters'
			for line in visible_text.splitlines(False):
				for match in pattern.finditer(line):
					info = ((line_num, match.start()), match.group(0))
					next_key = next(keys)
					self._all_labels[view].append((next_key, info))
					self._all_jumps[next_key] = (view, info)
				line_num += 1

	@property
	def all_labels(self):
		"""Get the previously indexed set of all labels."""
		return self._all_labels

	def get_jump_info(self, key):
		return self._all_jumps[key]
