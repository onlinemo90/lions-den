import datetime

from django import forms
from django.db import models

from .models import Species, Individual, SpeciesAttribute, IndividualAttribute


class BaseModelForm(forms.ModelForm):
	""""
		Base class for Forms that is compatible with custom DBs
		If not binding to a model instance, provide a zoo_id argument
	"""
	def __init__(self, *args, **kwargs):
		if 'zoo_id' in kwargs:
			zoo_id = kwargs.pop('zoo_id')
		elif 'instance' in kwargs:
			zoo_id = kwargs['instance'].zoo.id
		else:
			zoo_id=args[0]
		
		super().__init__(*args, **kwargs)
		
		fk_model_fields = [field for field in self._meta.model._meta.fields if isinstance(field, models.ForeignKey)]
		for field in fk_model_fields:
			if field.name in self.fields:
				self.fields[field.name] = forms.ModelChoiceField(queryset=field.related_model.objects.using(zoo_id).all())


class BaseSubjectForm(BaseModelForm):
	def save(self, fields_to_delete=[]):
		for field in fields_to_delete:
			field_type = type(getattr(self.instance, field))
			setattr(self.instance, field, field_type())
		super().save()


class SpeciesForm(BaseSubjectForm):
	image = forms.FileField()
	audio = forms.FileField()
	class Meta:
		model = Species
		fields = ['name', 'image', 'audio']
		labels = {
			'name': 'Name',
			'image': 'Image',
			'audio': 'Audio'
		}


class IndividualForm(BaseSubjectForm):
	image = forms.FileField()
	weight = forms.CharField(required=False)
	place_of_birth = forms.CharField(required=False)
	size = forms.CharField(required=False)
	dob = forms.DateField(
		widget=forms.widgets.SelectDateWidget(
			years=list(range(datetime.date.today().year, datetime.date.today().year - 101, -1)),
			empty_label=''
		),
		required=False,
		label='Date of Birth'
	)
	class Meta:
		model = Individual
		fields = ['name', 'image', 'gender', 'dob', 'place_of_birth', 'size', 'weight']
		labels = {
			'name': 'Name',
			'image': 'Image',
			'gender' : 'Gender',
			'weight' : 'Weight',
			'place_of_birth': 'Place of Birth',
			'size': 'Size'
		}


def get_subject_form(subject, *args, **kwargs):
	SubjectForm = SpeciesForm if isinstance(subject, Species) else IndividualForm
	return SubjectForm(instance=subject, *args, **kwargs)


def get_attributes_formset(subject, *args, **kwargs):
	SubjectAttribute = SpeciesAttribute if isinstance(subject, Species) else IndividualAttribute
	
	# Define form for displaying/editing each attribute
	class SubjectAttributeForm(BaseModelForm):
		class Meta:
			model = SubjectAttribute
			fields = ('category', 'attribute')
			labels = {'category': 'Header', 'attribute': 'Text'}
		
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.empty_permitted = False
			
			# Set labels correctly - for some reason Django screws this up
			for field, label in self._meta.labels.items():
				self.fields[field].label = label
			self.fields['category'].empty_label = ''
	
	
	# Define formset for multiple attributes
	BaseSubjectAttributesFormSet = forms.modelformset_factory(
		SubjectAttribute,
		form=SubjectAttributeForm,
		extra=0, # TODO: support additions - breaks formset validation
		can_delete=True,
		can_order=False
	)
	
	# Define formset for attributes specific to a subject (Species or Individual)
	class SubjectAttributesFormSet(BaseSubjectAttributesFormSet):
		def __init__(self, subject, *args, **kwargs):
			super().__init__(
				queryset=SubjectAttribute.objects.using(subject.zoo.id).filter(subject_id=subject.id).all(),
				form_kwargs={'zoo_id': subject.zoo.id},
				*args, **kwargs
			)
			
	return SubjectAttributesFormSet(subject, *args, **kwargs)