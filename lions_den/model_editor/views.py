from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

from .models import Species, Individual
from .forms import SpeciesForm, IndividualForm, AttributeCategoryForm, get_attributes_formset, get_new_attribute_form, get_attribute_categories_formset

# Base Views---------------------------------------------------------
class BaseZooView(LoginRequiredMixin, View):
	def dispatch(self, request, *args, **kwargs):
		""" Restrict access to view only to logged-in users with access to the specific zoo """
		# Get request and zoo_id arguments
		zoo_id = kwargs['zoo_id'] if 'zoo_id' in kwargs else args[0]
		
		# Check user permissions
		if not (request.user.is_authenticated and request.user.has_access(zoo_id=zoo_id)):
			return redirect('home')
		
		# Dispatch as usual but if an AJAX request, then redirect to [http_method]_ajax
		if request.method.lower() in self.http_method_names:
			method_name = request.method.lower()
			if request.is_ajax():
				method_name += '_ajax'
			handler = getattr(self, method_name, self.http_method_not_allowed)
		else:
			handler = self.http_method_not_allowed
		return handler(request, *args, **kwargs)
	
	def get_zoo(self, zoo_id):
		return Zoo.objects.filter(id=zoo_id).get()


class SubjectPageView(BaseZooView):
	template_name = 'model_editor/subject.html'
	
	def get_subject(self, zoo_id, subject_id):
		return self.model.objects.using(zoo_id).filter(id=subject_id).get()
	
	def get_forms(self, request, subject):
		request_data = request.POST if request.POST else None
		request_files = request.FILES if request.FILES else None
		
		subject_form_class = SpeciesForm if isinstance(subject, Species) else IndividualForm
		subject_form = subject_form_class(data=request_data, files=request_files, instance=subject)
		attributes_formset = get_attributes_formset(data=request_data, files=request_files, subject=subject, prefix='attributes')
		return subject_form, attributes_formset
	
	def get(self, request, zoo_id, subject_id):
		subject = self.get_subject(zoo_id, subject_id)
		subject_form, attributes_formset = self.get_forms(request=request, subject=subject)
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': self.get_zoo(zoo_id),
				'subject': subject,
				'subject_form': subject_form,
				'attributes_formset': attributes_formset
			}
		)
	
	def get_ajax(self, request, zoo_id, subject_id):
		if 'modal_new_attribute' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'Add attribute',
					'form': get_new_attribute_form(subject=self.get_subject(zoo_id, subject_id), prefix='new_attribute'),
					'submit_btn_name': 'submit_new_attribute'
				}
			)
		elif 'modal_qr_code' in request.GET:
			return render(
				request=request,
				template_name='model_editor/modals/qrcode_modal.html',
				context={
					'subject': self.get_subject(zoo_id, subject_id)
				}
			)
	
	def post(self, request, zoo_id, subject_id):
		subject = self.get_subject(zoo_id, subject_id)
		if 'submit_subject' in request.POST:
			subject_form, attributes_formset = self.get_forms(request=request, subject=subject)
			if subject_form.is_valid() and attributes_formset.is_valid():
				subject_form.save()
				attributes_formset.save()
				request.POST = None
		
		elif 'submit_new_attribute' in request.POST:
			new_attribute_form = get_new_attribute_form(subject=self.get_subject(zoo_id, subject_id), data=request.POST, prefix='new_attribute')
			if new_attribute_form.is_valid():
				new_attribute_form.save()
		
		return self.get(request, zoo_id, subject_id)
	
	def post_ajax(self, request, zoo_id, subject_id):
		return JsonResponse({'image_src': self.model.image.field.from_file(request.FILES["image"]).url })


class SubjectsListView(BaseZooView):
	def post_ajax(self, request, zoo_id):
		return JsonResponse({'image_src': self.model.image.field.from_file(request.FILES["image"]).url })

# Renderable Views---------------------------------------------------
class ZoosIndexView(LoginRequiredMixin, View):
	def get(self, request):
		if len(request.user.allowed_zoos) == 1:
			return redirect(request.user.allowed_zoos[0].id + '/')
		return render(
			request=request,
			template_name = 'model_editor/zoos_index.html',
			context={'zoos': request.user.allowed_zoos}
		)


class ZooHomeView(BaseZooView):
	template_name = 'model_editor/zoo.html'
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name=self.template_name,
			context={'zoo': self.get_zoo(zoo_id)}
		)
	
	def get_ajax(self, request, zoo_id):
		if 'modal_zoo_commit' in request.GET:
			return render(
				request=request,
				template_name='model_editor/modals/zoo_commit_modal.html'
			)
	
	def post(self, request, zoo_id):
		try:
			self.get_zoo(zoo_id).commit_to_zooverse(request.user)
			messages.add_message(request, messages.INFO, 'Your commit request has been received and will be processed within 30 days')
		except Exception as e:
			messages.add_message(request, messages.ERROR, str(e))
		return self.get(request, zoo_id)


class SpeciesListView(SubjectsListView):
	model = Species
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name='model_editor/species_list.html',
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': Species.objects.using(zoo_id).order_by('name').all()
			}
		)
	
	def get_ajax(self, request, zoo_id):
		if 'modal_new_subject' in request.GET:
			return render(
				request=request,
				template_name='model_editor/modals/new_subject_modal_form.html',
				context={
					'title': 'New Species',
					'form': SpeciesForm(zoo_id=zoo_id),
					'submit_btn_name': 'submit_new_subject'
				}
			)
	
	def post(self, request, zoo_id):
		if 'submit_new_subject' in request.POST:
			new_species_form = SpeciesForm(data=request.POST, files=request.FILES, zoo_id=zoo_id)
			if new_species_form.is_valid():
				new_species_form.save()
		return self.get(request, zoo_id)


class IndividualsListView(SubjectsListView):
	model = Individual
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name='model_editor/individuals_list.html',
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': Individual.objects.using(zoo_id).order_by('name'),
				'species_list': Species.objects.using(zoo_id).order_by('name')
			}
		)
	
	def get_ajax(self, request, zoo_id):
		if 'species_filter' in request.GET:
			individuals_shown = Individual.objects.using(zoo_id).order_by('name')
			if request.GET.get('species_id'):
				individuals_shown = individuals_shown.filter(species__id=request.GET['species_id'])
			return render(
				request=request,
				template_name='model_editor/subject_table.html',
				context={'subjects': individuals_shown}
			)
		elif 'modal_new_subject' in request.GET:
			return render(
				request=request,
				template_name='model_editor/modals/new_subject_modal_form.html',
				context={
					'title': 'New Individual',
					'form': IndividualForm(zoo_id=zoo_id),
					'submit_btn_name': 'submit_new_subject'
				}
			)
	
	def post(self, request, zoo_id):
		if 'submit_new_subject' in request.POST:
			new_individual_form = IndividualForm(data=request.POST, files=request.FILES, zoo_id=zoo_id)
			if new_individual_form.is_valid():
				new_individual_form.save()
		return self.get(request, zoo_id)


class SpeciesPageView(SubjectPageView):
	model = Species


class IndividualPageView(SubjectPageView):
	model = Individual


class AttributeCategoryListView(BaseZooView):
	template_name = 'model_editor/attribute_category_list.html'
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': self.get_zoo(zoo_id),
				'formset': get_attribute_categories_formset(zoo_id=zoo_id)
			}
		)
	
	def get_ajax(self, request, zoo_id):
		if 'modal_new_category' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form.html',
				context={
					'title': 'New Attribute Category',
					'form': AttributeCategoryForm(zoo_id=zoo_id),
					'submit_btn_name': 'submit_new_category'
				}
			)
	
	def post(self, request, zoo_id):
		if 'submit_categories' in request.POST:
			categories_formset = get_attribute_categories_formset(zoo_id=zoo_id, data=request.POST)
			if categories_formset.is_valid():
				categories_formset.save()
		elif 'submit_new_category' in request.POST:
			new_category_form = AttributeCategoryForm(zoo_id=zoo_id, data=request.POST)
			if new_category_form.is_valid():
				new_category_form.save()
		
		return self.get(request, zoo_id)
