import io
import base64
import enum

from django.db import models

from .utils.qrcode_creator import create_request_qrcode


class Zoo(models.Model):
	_id = models.IntegerField(primary_key=True)
	id = models.CharField(unique=True, max_length=10)
	name = models.CharField(unique=True, max_length=128)
	encryption_key = models.CharField(unique=True, max_length=35)
	image = models.ImageField()
	date_joined = models.DateField(auto_now_add=True)
	
	def __str__(self):
		return self.name


#---------------------------------------------------------------------------------------

class Gender(enum.Enum):
	MALE = 'M'
	FEMALE = 'F'


class BlobField(models.BinaryField):
	def from_db_value(self, value, expression, connection):
		return io.BytesIO(value) if value is not None else None
	
	def get_prep_value(self, value):
		return value.read()


class DefaultCharField(models.CharField):
	def __init__(self, *args, **kwargs):
		if 'max_length' not in kwargs:
			kwargs['max_length'] = 16
		super().__init__(*args, **kwargs)


class AbstractBaseModel(models.Model):
	id = models.AutoField(db_column='_id', primary_key=True)
	
	class Meta:
		abstract = True
	
	def __getattribute__(self, name):
		try:
			return super().__getattribute__(name)
		except AttributeError:
			try:
				blob_field = name.removesuffix('_str')
				return base64.b64encode(super().__getattribute__(blob_field).read()).decode()
			except:
				return super().__getattribute__(name) # raise original exception
	
	@property
	def zoo(self):
		assert self._state.db is not None, f'{self} does not belong to any zoo'
		return Zoo.objects.filter(id=self._state.db).first()


class Species(AbstractBaseModel):
	name = DefaultCharField()
	image = BlobField(editable=True, null=True, blank=False)
	audio = BlobField(editable=True, null=True, blank=True)
	
	class Meta:
		db_table = 'SPECIES'
	
	def __str__(self):
		return self.name
	
	@property
	def qrcode(self):
		return create_request_qrcode(
			zoo=self.zoo,
			request='I|' + str(self.id)
		)


class Individual(AbstractBaseModel):
	species = models.ForeignKey(Species, related_name='individuals', on_delete=models.CASCADE) # If the species is deleted, so are the related individuals
	name = DefaultCharField()
	dob = models.DateField()
	place_of_birth = DefaultCharField()
	weight = DefaultCharField()
	image = BlobField(editable=True, null=True, blank=False)
	size = DefaultCharField()
	gender = DefaultCharField(
		choices=( [(None, '')] + [(gender.value, gender.name.title()) for gender in Gender] ),
		blank=True, null=True
	)
	
	class Meta:
		db_table = 'INDIVIDUAL'
	
	def __str__(self):
		return self.name


class AttributeCategory(AbstractBaseModel):
	name = models.TextField()
	priority = models.TextField(unique=True)
	class Meta: db_table = 'ATTRIBUTE_CATEGORY'
	def __str__(self): return self.name


class AbstractAttribute(AbstractBaseModel):
	category = models.ForeignKey(AttributeCategory, on_delete=models.CASCADE)
	attribute = models.TextField()
	class Meta: abstract = True
	def __str__(self): return f'{self.category} -> {self.attribute}'


class SpeciesAttribute(AbstractAttribute):
	subject = models.ForeignKey(Species, related_name='attributes', on_delete=models.CASCADE)
	class Meta: db_table = 'SPECIES_ATTRIBUTES'


class IndividualAttribute(AbstractAttribute):
	subject = models.ForeignKey(Individual, related_name='attributes', on_delete=models.CASCADE)
	class Meta: db_table = 'INDIVIDUALS_ATTRIBUTES'


