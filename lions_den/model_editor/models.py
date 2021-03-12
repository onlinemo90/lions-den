import enum

from django.db import models

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

from .model_fields import DefaultCharField, ImageBlobField, AudioBlobField
from .utils.qrcode_creator import create_request_qrcode


class Gender(enum.Enum):
	MALE = 'M'
	FEMALE = 'F'


class AbstractBaseModel(models.Model):
	id = models.AutoField(db_column='_id', primary_key=True)
	
	class Meta:
		abstract = True
	
	@property
	def zoo(self):
		assert self._state.db is not None, f'{self} does not belong to any zoo'
		return Zoo.objects.filter(id=self._state.db).first()


class Species(AbstractBaseModel):
	name = DefaultCharField()
	image = ImageBlobField(size=(256, 192), editable=True, null=True, blank=False)
	audio = AudioBlobField(editable=True, null=True, blank=True)
	
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
	species = models.ForeignKey(Species, related_name='individuals', on_delete=models.CASCADE)  # If the species is deleted, so are the related individuals
	name = DefaultCharField()
	dob = models.DateField()
	place_of_birth = DefaultCharField()
	weight = DefaultCharField()
	image = ImageBlobField(size=(256, 192), editable=True, null=True, blank=False)
	size = DefaultCharField()
	gender = DefaultCharField(
		choices=([(None, '')] + [(gender.value, gender.name.title()) for gender in Gender]),
		blank=True, null=True
	)
	
	class Meta:
		db_table = 'INDIVIDUAL'
	
	def __str__(self):
		return self.name


class AttributeCategory(AbstractBaseModel):
	name = DefaultCharField()
	priority = models.PositiveIntegerField(unique=True)
	
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


