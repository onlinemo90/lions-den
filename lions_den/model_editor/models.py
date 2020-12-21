import base64
from .utils.qrcode_creator import create_request_qrcode

from django.db import models

from .zoos import zoos

class BaseModel(models.Model):
	class Meta:
		abstract = True
	
	@property
	def db(self):
		""""
			Returns the ID of the database from which the model instance has been retrieved from/saved to
			 If model instance was instantiated rather than queried from DB, then will return None
		 """
		return self._state.db
	
	def _get_text_field(self, field_name):
		field = getattr(self, field_name)
		return field if field else ''
	
	def _get_blob_field(self, field_name):
		field = getattr(self, field_name)
		return base64.b64encode(field).decode() if field is not None else None


class Species(BaseModel):
	id = models.IntegerField(primary_key=True, db_column='_id')
	_name = models.TextField(db_column='name')
	_image = models.BinaryField(db_column='image')
	_description = models.TextField(db_column='description')
	_audio = models.TextField(db_column='audio')
	
	class Meta:
		db_table = 'SPECIES'
	
	def __str__(self):
		return self.name
	
	@property
	def name(self): return self._get_text_field('_name')
	
	@property
	def image(self): return self._get_blob_field('_image')

	@property
	def description(self): return self._get_text_field('_description')
	
	@property
	def audio(self): return self._get_blob_field('_audio')
	
	@property
	def qrcode(self):
		assert self.db is not None, 'Cannot create QR Code for non-DB Species instance'
		return create_request_qrcode(
			zoo=zoos[self.db],
			request='I|' + str(self.id)
		)


class Individual(BaseModel):
	id = models.IntegerField(primary_key=True, db_column='_id')
	species_id = models.ForeignKey(Species, on_delete=models.CASCADE) # If the species is deleted, so are the related individuals
	_name = models.TextField(db_column='name')
	_dob = models.IntegerField(db_column='dob')
	_place_of_birth = models.TextField(db_column='place_of_birth')
	_gender = models.TextField(db_column='gender')
	_weight = models.TextField(db_column='weight')
	_image = models.TextField(db_column='image')
	
	class Meta:
		db_table = 'INDIVIDUAL'
	
	def __str__(self):
		return self.name
	
	@property
	def name(self): return self._get_text_field('_name')
	
	@property
	def dob(self): return self._get_text_field('_dob')
	
	@property
	def place_of_birth(self): return self._get_text_field('_place_of_birth')
	
	@property
	def gender(self): return self._get_text_field('_gender')
	
	@property
	def weight(self): return self._get_text_field('_weight')
	
	@property
	def image(self): return self._get_blob_field('_image')
