from django.conf import settings as project_settings

class _Zoo:
	def __init__(self, id, name, encryption_key):
		self.id = id
		self.name = name
		self.encryption_key = encryption_key

zoos = {
	'test' : _Zoo(id='test', name='Test Zoo', encryption_key='12345678901234567890123456789012'),
}

# Confirm that zoos and databases match up
if not len(zoos.keys() & project_settings.DATABASES.keys()) == len(zoos.keys()) == len(project_settings.DATABASES.keys()) - 1:
	raise Exception('Defined Zoos and installed databases do not match([' +
					', '.join([zoo_id for zoo_id in zoos.keys()]) +
					'] vs [' +
					', '.join([db_id for db_id in project_settings.DATABASES.keys() if db_id != 'default']) +
					'])'
	)