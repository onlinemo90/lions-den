import datetime

from django import forms
from django.forms.models import modelformset_factory

from .models import Species, Individual, Group, AttributeCategory, ZooLocation
from .form_fields import ImageBlobField, AudioBlobField


class BaseModelForm(forms.ModelForm):
	""""
		Base class for Forms that is compatible with custom DBs
		If not binding to a model instance, provide a zoo_id argument
	"""
	def __init__(self, *args, **kwargs):
		if 'zoo_id' in kwargs:
			self.zoo_id = kwargs.pop('zoo_id')
		elif 'instance' in kwargs:
			self.zoo_id = kwargs['instance'].zoo.id
		else:
			raise Exception('zoo_id must be given to create zoo-related form')

		if 'instance' not in kwargs:
			super().__init__(*args, **kwargs)
			self.instance._state.db = self.zoo_id
		else:
			super().__init__(*args, **kwargs)
		self.instance._meta.default_manager._db = self.zoo_id  # needed to ensure uniqueness constraints can be validated
		
		if 'location' in self.fields:
			self.fields['location'] = forms.ModelChoiceField(
				queryset=ZooLocation.objects.using(self.zoo_id).all(),
				required=self.fields['location'].required,
				empty_label=''
			)


class BaseSubjectForm(BaseModelForm):
	def __init__(self, *args, **kwargs):
		# Stabilising HTML element ID generation to allow Javascript ID matching on field HTML elements
		kwargs['auto_id'] = 'id_subject_%s'
		if 'prefix' in kwargs:
			raise Exception("""
				A prefix is not allowed for SubjectForms.
				Unless you're trying to display multiple SubjectForms in one page, this shouldn't be needed.
			""")
		super().__init__(*args, **kwargs)


class SpeciesForm(BaseSubjectForm):
	image = ImageBlobField()
	audio = AudioBlobField(required=False)
	location = forms.ModelChoiceField(queryset=None, required=False)
	weight = forms.CharField(required=False)
	size = forms.CharField(required=False)
	
	class Meta:
		model = Species
		fields = ('name', 'image', 'audio', 'location', 'size', 'weight')
		labels = {
			'name': 'Name',
			'image': 'Image',
			'audio': 'Audio',
			'location': 'Location',
			'size': 'Size',
			'weight': 'Weight'
		}


class IndividualForm(BaseSubjectForm):
	species = forms.ModelChoiceField(queryset=None) # set in __init__
	image = ImageBlobField()
	place_of_birth = forms.CharField(required=False)
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
		fields = ('species', 'name', 'image', 'gender', 'dob', 'place_of_birth')
		labels = {
			'species': 'Species',
			'name': 'Name',
			'image': 'Image',
			'gender': 'Gender',
			'place_of_birth': 'Place of Birth'
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# Allow form to be used both for editing existing individuals and for creating new ones
		if 'instance' in kwargs:
			del self.fields['species']
		else:
			self.fields['species'] = forms.ModelChoiceField(empty_label='', queryset=Species.objects.using(kwargs['zoo_id']).all())


class GroupForm(BaseSubjectForm):
	image = ImageBlobField()
	audio = AudioBlobField(required=False)
	
	class Meta:
		model = Group
		fields = ('name', 'image', 'audio', 'species', 'individuals')
		labels = {
			'name': 'Name',
			'image': 'Image',
			'audio': 'Audio'
		}
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		self.fields['species'] = forms.ModelMultipleChoiceField(queryset=Species.objects.using(self.zoo_id).all(), required=False)
		self.fields['individuals'] = forms.ModelMultipleChoiceField(queryset=Individual.objects.using(self.zoo_id).all(), required=False)
		
		# Hide foreign key fields (front-end handled by Javascript)
		self.fields['species'].widget.attrs.update({'hidden': True})
		self.fields['individuals'].widget.attrs.update({'hidden': True})


class NewZooLocationForm(BaseModelForm):
	class Meta:
		model = ZooLocation
		fields = ('name',)
	
	def save(self, commit=True):
		self.instance.coordinates = self.instance.zoo.coordinates
		super().save(commit)


class ZooLocationForm(BaseModelForm):
	class Meta:
		model = ZooLocation
		fields = ('name', 'coordinates')
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['coordinates'].widget.attrs.update({'disabled': ''}) # prevent manual change of coordinates


class AvailableSubjectAttributeCategoriesForm(BaseModelForm):
	class Meta:
		model = AttributeCategory
		fields = ('name',)
	
	def __init__(self, subject, exclude_categories, *args, **kwargs):
		super().__init__(zoo_id=subject.zoo.id, *args, **kwargs)
		
		used_categories = [attribute.category.id for attribute in subject.attributes.all()] + exclude_categories
		self.fields['name'] = forms.ModelChoiceField(
			label='Category',
			empty_label='',
			queryset=AttributeCategory.objects.using(subject.zoo.id).exclude(id__in=used_categories)
		)
	
	def save(self, commit=True):
		raise AttributeError('This form is not meant to alter data!')


def get_attributes_formset(subject, *args, **kwargs):
	# Define form for displaying/editing each attribute
	class SubjectAttributeForm(BaseModelForm):
		class Meta:
			model = subject.__class__.get_attribute_model()
			fields = ('category', 'attribute')
		
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)

			self.instance.subject_id = subject.id

			# Set additional hidden fields to allow dynamic adding of new forms
			if hasattr(self.instance, 'category'): # when basing on an existing attribute instance
				self.fields['attribute'].label = self.instance.category.name
				initial_category_name = self.instance.category.name
				initial_category_position = self.instance.category.position
			elif hasattr(self, 'data') and self.data: # when reloading the form if invalid
				initial_category_name = self.data.get(self.prefix + '-category_name')
				self.fields['attribute'].label = initial_category_name
				initial_category_position = self.data.get(self.prefix + '-category_position')
			else: # for formset.empty_form, since it will not have a category bound to it
				self.fields['attribute'].label = '__CATEGORY_NAME_PLACEHOLDER__'
				initial_category_name = ''
				initial_category_position = ''
			
			self.fields['category'] = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=AttributeCategory.objects.using(self.zoo_id).all())
			self.fields['category_name'] = forms.CharField(widget=forms.HiddenInput, initial=initial_category_name)
			self.fields['category_position'] = forms.CharField(widget=forms.HiddenInput, initial=initial_category_position)
	
	
	# Define formset for multiple attributes
	BaseSubjectAttributesFormSet = forms.modelformset_factory(
		subject.__class__.get_attribute_model(),
		form=SubjectAttributeForm,
		extra=0,
		can_delete=True,
		can_order=False,
		max_num=AttributeCategory.objects.using(subject.zoo.id).count()
	)
	
	# Define formset for attributes specific to a subject (Species or Individual)
	class SubjectAttributesFormSet(BaseSubjectAttributesFormSet):
		def __init__(self, subject, *args, **kwargs):
			super().__init__(
				queryset=subject.__class__.get_attribute_model().objects.using(subject.zoo.id).filter(subject_id=subject.id).all(),
				form_kwargs={'zoo_id': subject.zoo.id},
				*args, **kwargs
			)
		
		def __iter__(self):
			"""" Defines the order in which forms are rendered """
			return sorted(self.forms, key=lambda form : str(form.fields['category_position'].initial)).__iter__()
	
	return SubjectAttributesFormSet(subject, *args, **kwargs)


class AttributeCategoryForm(BaseModelForm):
	class Meta:
		model = AttributeCategory
		fields = ('name',)


def get_attribute_categories_formset(zoo_id, *args, **kwargs):
	BaseAttributeCategoriesFormset = modelformset_factory(
		AttributeCategory,
		form=AttributeCategoryForm,
		extra=0,
		can_delete=True,
		can_order=True
	)
	
	class AttributeCategoriesFormset(BaseAttributeCategoriesFormset):
		def __init__(self, zoo_id, *args, **kwargs):
			super().__init__(
				queryset=AttributeCategory.objects.using(zoo_id).order_by('position').all(),
				form_kwargs={'zoo_id': zoo_id},
				*args, **kwargs
			)
		
		def save(self, commit=True):
			super().save(commit)
			
			def set_categories_position(start_position):
				current_position = start_position
				for form in self.ordered_forms:
					form.instance.position = current_position
					current_position += 1
					form.instance.save()
			
			set_categories_position(len(self.forms) + 1)
			set_categories_position(1)
	
	return AttributeCategoriesFormset(zoo_id, *args, **kwargs)
