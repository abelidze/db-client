class MappingList(dict):
	def __call__(self, key, *args):
		self[key](*args)

	def __missing__(self, key):
		print('Unrecognized mapping for key: {}'.format(key))
		return lambda *args: 0


processAction = MappingList({
	# 'sql': None,
	# 'connect': None
})