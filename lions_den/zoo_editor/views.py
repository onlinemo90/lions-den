import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

# noinspection PyUnresolvedReferences
from zoo_auth.models import Zoo

from .models import Species, Individual, Group, AttributeCategory
from .forms import get_attributes_formset, get_attribute_categories_formset, AvailableSubjectAttributeCategoriesForm


# Base Views---------------------------------------------------------
class BaseZooView(LoginRequiredMixin, View):
	@method_decorator(never_cache)
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
	
	def redirect_to_self(self, request):
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class SubjectPageView(BaseZooView):
	template_name = 'zoo_editor/subject.html'
	
	def get_subject(self, zoo_id, subject_id):
		return self.model.objects.using(zoo_id).filter(id=subject_id).get()
	
	def get_forms(self, request, subject):
		request_data = request.POST if request.POST else None
		request_files = request.FILES if request.FILES else None
		
		subject_form = self.model.form(data=request_data, files=request_files, instance=subject)
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
		subject = self.get_subject(zoo_id, subject_id)
		if 'modal_new_attribute' in request.GET:
			return render(
				request=request,
				template_name='utils/modals/modal_form_ajax.html',
				context={
					'title': 'Add Attribute',
					'form': AvailableSubjectAttributeCategoriesForm(
						subject=subject,
						exclude_categories=json.loads(request.GET.get('exclude_category_ids'))
					),
					'submit_btn_name': 'add_new_attribute',
					'ajax_success_function_name': 'addSubjectAttributeForm'
				}
			)
		elif 'modal_qr_code' in request.GET:
			return render(
				request=request,
				template_name='zoo_editor/modals/qrcode_modal.html',
				context={
					'subject': subject
				}
			)
		else:
			return self.get_ajax_sub(request, zoo_id, subject_id)
	
	def post(self, request, zoo_id, subject_id):
		subject = self.get_subject(zoo_id, subject_id)
		if 'submit_subject' in request.POST:
			subject_form, attributes_formset = self.get_forms(request=request, subject=subject)
			if subject_form.is_valid() and attributes_formset.is_valid():
				subject_form.save()
				attributes_formset.save()
				return self.redirect_to_self(request)
		
		return self.get(request, zoo_id, subject_id)
	
	def post_ajax(self, request, zoo_id, subject_id):
		if 'update_image_display' in request.POST:
			try:
				return JsonResponse({'image_src': self.model.image.field.from_file(request.FILES["image"]).url })
			except:
				return JsonResponse({})
		elif 'add_new_attribute' in request.POST:
			if 'name' in request.POST: # name field actually returns the category id
				attribute_category = AttributeCategory.objects.using(zoo_id).get(id=request.POST.get('name'))
				return JsonResponse({
					'category_id': attribute_category.id,
					'category_name': attribute_category.name,
					'category_position': attribute_category.position
				})
		else:
			return self.post_ajax_sub(request, zoo_id, subject_id)


class SubjectsListView(BaseZooView):
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': self.model.objects.using(zoo_id).all()
			}
		)

	def get_ajax(self, request, zoo_id, form=None):
		if 'modal_new_subject' in request.GET:
			if not form: # invalid form
				form = self.model.form(zoo_id=zoo_id)
			return render(
				request=request,
				template_name='zoo_editor/modals/new_subject_modal_form.html',
				context={
					'title': f'New {self.model.get_type_str().capitalize()}',
					'form': form,
					'submit_btn_name': 'modal_new_subject',
					'ajax_success_function_name': 'newSubjectFormSuccess'
				}
			)
		elif 'modal_delete_subject' in request.GET:
			return render(
				request=request,
				template_name='zoo_editor/modals/delete_subject_modal.html',
				context={
					'subject': self.model.objects.using(zoo_id).filter(id=request.GET.get('subject_id')).get()
				}
			)
		else:
			return self.get_ajax_sub(request, zoo_id)

	def get_ajax_sub(self, request, zoo_id):
		""" Method for subclasses to implement their specific get_ajax logic without overwriting the base class one """
		return None

	def post(self, request, zoo_id):
		if 'submit_delete_subject' in request.POST:
			subject = self.model.objects.using(zoo_id).filter(id=request.POST.get('subject_id')).get()
			subject.delete()
			return self.redirect_to_self(request)

		return self.get(request, zoo_id)

	def post_ajax(self, request, zoo_id):
		if 'update_image_display' in request.POST:
			try:
				return JsonResponse({'image_src': self.model.image.field.from_file(request.FILES["image"]).url})
			except:
				return JsonResponse({})
		elif 'modal_new_subject' in request.POST:
			new_subject_form = self.model.form(data=request.POST, files=request.FILES, zoo_id=zoo_id)
			if new_subject_form.is_valid():
				new_subject_form.save()
				return JsonResponse({'form_valid': True})
			else:
				request.GET = request.POST
				return self.get_ajax(request, zoo_id, form=new_subject_form)


# Renderable Views---------------------------------------------------
class ZoosIndexView(LoginRequiredMixin, View):
	def get(self, request):
		if len(request.user.zoos) == 1:
			return redirect(request.user.zoos[0].id + '/')
		return render(
			request=request,
			template_name = 'zoo_editor/zoos_list.html',
			context={'zoos': request.user.zoos}
		)


class ZooHomeView(BaseZooView):
	template_name = 'zoo_editor/zoo.html'
	
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
				template_name='zoo_editor/modals/zoo_commit_modal.html'
			)
	
	def post(self, request, zoo_id):
		try:
			self.get_zoo(zoo_id).commit_to_zooverse(request.user)
			messages.info(request, 'Your commit request has been received and will be processed within 30 days')
			return self.redirect_to_self(request)
		except Exception as e:
			messages.error(request, str(e))
		return self.get(request, zoo_id)


class SpeciesListView(SubjectsListView):
	model = Species
	template_name = 'zoo_editor/species_list.html'


class IndividualsListView(SubjectsListView):
	model = Individual
	template_name = 'zoo_editor/individuals_list.html'
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': Individual.objects.using(zoo_id),
				'species_list': Species.objects.using(zoo_id)
			}
		)
	
	def get_ajax_sub(self, request, zoo_id):
		if 'species_filter' in request.GET:
			individuals_shown = Individual.objects.using(zoo_id)
			if request.GET.get('species_id'):
				individuals_shown = individuals_shown.filter(species__id=request.GET['species_id'])
			return render(
				request=request,
				template_name='zoo_editor/subject_table.html',
				context={'subjects': individuals_shown}
			)


class GroupsListView(SubjectsListView):
	model = Group
	template_name = 'zoo_editor/groups_list.html'
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': self.get_zoo(zoo_id),
				'subjects': Group.objects.using(zoo_id)
			}
		)


class SpeciesPageView(SubjectPageView):
	model = Species


class IndividualPageView(SubjectPageView):
	model = Individual


class GroupPageView(SubjectPageView):
	model = Group
	
	def get_ajax_sub(self, request, zoo_id, subject_id):
		group = self.get_subject(zoo_id, subject_id)
		members_type_str = request.GET.get('members_type')
		
		members = getattr(group, members_type_str).all()
		non_members = getattr(group, 'non_member_' + members_type_str)
		return render(
			request=request,
			template_name='zoo_editor/group_members.html',
			context={
				'title': 'Species' if members_type_str == 'species' else 'Individuals',
				'members_type' : members_type_str,
				'members': members,
				'non_members': non_members
			}
		)
	
	def post_ajax_sub(self, request, zoo_id, subject_id):
		group = self.get_subject(zoo_id, subject_id)
		if request.POST.get('action') == 'add':
			getattr(group, request.POST.get('members_type')).add(request.POST['id'])
			group.save()
		elif request.POST.get('action') == 'delete':
			getattr(group, request.POST.get('members_type')).remove(request.POST.get('id'))
			group.save()
		
		request.GET = request.POST # so self.get_ajax has easy access to request parameters
		return self.get_ajax(request, zoo_id, subject_id)


class AttributeCategoryListView(BaseZooView):
	template_name = 'zoo_editor/attribute_categories_list.html'
	
	def get(self, request, zoo_id):
		return render(
			request=request,
			template_name=self.template_name,
			context={
				'zoo': self.get_zoo(zoo_id),
				'formset': get_attribute_categories_formset(zoo_id=zoo_id, data=(request.POST if request.POST else None))
			}
		)
	
	def post(self, request, zoo_id):
		if 'submit_categories' in request.POST:
			categories_formset = get_attribute_categories_formset(zoo_id=zoo_id, data=request.POST)
			if categories_formset.is_valid():
				categories_formset.save()
				return self.redirect_to_self(request)
		
		return self.get(request, zoo_id)
