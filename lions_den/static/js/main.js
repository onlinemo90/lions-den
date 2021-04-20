// Load Bootstrap Toasts------------------------------------------------------------------------------------------------
window.addEventListener('load', function () {
	$('.toast').toast('show');
	$(document).ready(function(){
		$('[data-toggle="tooltip"]').tooltip();
	});
});
//----------------------------------------------------------------------------------------------------------------------

// Setup AJAX to support POST requests----------------------------------------------------------------------------------
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
//----------------------------------------------------------------------------------------------------------------------

// Modals---------------------------------------------------------------------------------------------------------------
function getModal(modalID, extraData){
	data = modalID;
	if (extraData){
		data += '&' + extraData;
	}
	$.ajax({
		type: 'GET',
		url: document.URL,
		data: data,
		success: function(response){
			if (document.getElementById('modal')){
				$('#modal').replaceWith(response);
			} else {
				$('main').append(response);
			}
			$('#modal').modal('show');
			initDynamicBlobFieldDisplay(); // allow for newly created image and audio fields to dynamically update
		},
	});
}

function submitModalForm(formName, successFunction){ // Submit AJAX modal form
	formData = new FormData($('#modalForm')[0]);
	formData.append(formName, '');
	$.ajax({
		type: 'POST',
		enctype: 'multipart/form-data',
		url: document.URL,
		data: formData,
		processData: false,
		contentType: false,
		success: successFunction
	});
}
//----------------------------------------------------------------------------------------------------------------------

// Dynamic image & audio updating in subject forms----------------------------------------------------------------------
function setDynamicBlobDisplay(displayID, widgetID, audioControlID, updateFunction) {
	let reloadAudio = function(){ if (audioControlID){ $("#" + audioControlID)[0].load() } };
	var initialValue = document.getElementById(displayID).src;
	document.querySelector('#' + widgetID).addEventListener('change', function() {
		var file = document.getElementById(widgetID).files[0];
		var displayElement = document.getElementById(displayID);
		if (file){
			var reader  = new FileReader();
			reader.onload = updateFunction;
			reader.readAsDataURL(file);
		} else {
			displayElement.src = initialValue;
			reloadAudio();
		}
	});
}

function setDynamicImageDisplay(displayID, widgetID, audioControlID){
	return setDynamicBlobDisplay(displayID, widgetID, null,
		function(e){
			var file = document.getElementById(widgetID).files[0];
			let formdata = new FormData();
			if (formdata) {
				formdata.append("image", file);
				formdata.append("update_image_display", null);
				$.ajax({
					url: document.URL,
					type: "POST",
					data: formdata,
					processData: false,
					contentType: false,
					success: function(data){ document.getElementById(displayID).src = data['image_src'] },
					error: function() {}
				});
			}
		}
	)
}

function setDynamicAudioDisplay(displayID, widgetID, audioControlID){
	return setDynamicBlobDisplay(displayID, widgetID, null,
		function(e){
			$("#" + audioControlID)[0].load();
			document.getElementById(displayID).src = e.target.result;
		}
	)
}

function initDynamicBlobFieldDisplay(){
	if (document.getElementById("id_subject_image")){
		setDynamicImageDisplay("id_subject_image-display", "id_subject_image");
	}

	if (document.getElementById("id_subject_audio")){
		setDynamicAudioDisplay("id_subject_audio-display", "id_subject_audio", "id_subject_audio-display_controls");
	}
}

document.addEventListener("DOMContentLoaded", function(){
	initDynamicBlobFieldDisplay();
});
//----------------------------------------------------------------------------------------------------------------------

// Subject Attributes Formset-------------------------------------------------------------------------------------------
function addSubjectAttributeForm(ajaxResponse){
	newCategoryID = ajaxResponse['category_id']
	newCategoryName = ajaxResponse['category_name'];
	newCategoryPosition = ajaxResponse['category_position'];

	FORM_PREFIX = 'attributes-'
	FORM_ID_PREFIX = 'id_' + FORM_PREFIX

	// Prepare new form from empty template form
	numForms = parseInt($('#' + FORM_ID_PREFIX + 'TOTAL_FORMS').val());
	newFormHTML = $('#EMPTY_FORM_TEMPLATE').html()
		.replaceAll('__prefix__', numForms)
		.replaceAll('__CATEGORY_NAME_PLACEHOLDER__', newCategoryName);

	// Place form in correct order (by category position)
	formPlaced = false;
	$('#attributes_formset_section div[id^=attribute_form_]').each(function(){
		formCategoryPosition = $('input[id$=category_position]', this).val();
		if (newCategoryPosition < formCategoryPosition){
			$(this).before(newFormHTML);
			formPlaced = true;
			return false; // break out of $.each
		}
	});
	if (!formPlaced){
		$('#attributes_formset_section').append(newFormHTML);
	}

	// Set new form values
	$('input[id=' + FORM_ID_PREFIX + numForms + '-category]').val(newCategoryID);
	$('input[id=' + FORM_ID_PREFIX + numForms + '-category_name]').val(newCategoryName);
	$('input[id=' + FORM_ID_PREFIX + numForms + '-category_position]').val(newCategoryPosition);

	// Increment form count
	numForms += 1;
	$('#' + FORM_ID_PREFIX + 'TOTAL_FORMS').val(numForms);

	// Hide 'add new attribute' button if no further categories are available
	if ((numForms) == $('#' + FORM_ID_PREFIX + 'MAX_NUM_FORMS').val()){
		$('#add_attribute_btn').hide();
	}

	// Hide modal
	$('#modal').modal('hide');

	// Prevent category from being added in this session
	_alreadyUsedCategoryIDs.push(newCategoryID);
}

var _alreadyUsedCategoryIDs = [];
function getAlreadyUsedCategoryIDs(){
	/*
		Provides a GET parameter containing a list of attribute category IDs added in the current session.
		Meant to be added to the AJAX GET request when requesting the list of attribute categories
		the user can still add to the subject.
	*/
	return 'exclude_category_ids=' + JSON.stringify(_alreadyUsedCategoryIDs);
}
//----------------------------------------------------------------------------------------------------------------------

// New Subject Form-----------------------------------------------------------------------------------------------------
function newSubjectFormSuccess(response){
	if (response['form_valid']){
		window.location = window.location;
	} else {
		newModal = $(response);
		newModalContents = $('.modal-content', newModal);
		$('#modal .modal-content').html(newModalContents.html());
		initDynamicBlobFieldDisplay();
	}
}
//----------------------------------------------------------------------------------------------------------------------

// Filtering Individuals List by Species--------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function(){
	if (document.getElementById('select_species')){
		$('#select_species').on('change', function(){
			$.ajax({
				type: 'GET',
				url: document.URL,
				data: 'species_filter&species_id=' + $(this).val(),
				success: function (response) {
					$('#subject-table').replaceWith(response);
				}
			});
		});
	}
});
//----------------------------------------------------------------------------------------------------------------------

// Group Page - Show and Edit Members-----------------------------------------------------------------------------------
function addMemberToGroup(membersType){
	memberId = document.getElementById('group_select_' + membersType).value;
	if (memberId){
		$('#id_subject_' + membersType + ' option[value=' + memberId + ']').attr('selected', true); // select in hidden form field
		$('#group_list_' + membersType + ' li[value=' + memberId + ']').prop('hidden', false); // show in members list
		$('#group_select_' + membersType + ' option[value=' + memberId + ']').prop('hidden', true); // hide from non-members select

		$('#group_select_' + membersType).prop('selectedIndex', 0); // reset selection
	}
}

function removeMemberFromGroup(membersType, memberId){
	$('#id_subject_' + membersType + ' option[value=' + memberId + ']').attr('selected', false); // unselect in hidden form field
	$('#group_list_' + membersType + ' li[value=' + memberId + ']').prop('hidden', true); // hide from members list
	$('#group_select_' + membersType + ' option[value=' + memberId + ']').prop('hidden', false); // show in non-members select
}

function createGroupListItem(membersType, text, value){
	let memberListItem = document.getElementById('GROUP_LIST_ITEM_TEMPLATE_' + membersType).cloneNode(true);
	memberListItem.removeAttribute('id');
	memberListItem.value = value;
	memberListItem.innerHTML = memberListItem.innerHTML.replaceAll('[VALUE]', value).replaceAll('[MEMBER_NAME]', text);
	return memberListItem;
}

function initGroupMembersDisplay(membersType){
	for (let option of document.getElementById('id_subject_' + membersType).options){
		// Non-members select
		let selectOption = document.createElement('option');
		selectOption.text = option.innerHTML;
		selectOption.value = option.value;

		// Members list
		let memberListItem = createGroupListItem(membersType, option.innerHTML, option.value);

		if (option.selected){
			memberListItem.removeAttribute('hidden'); // un-hide from list
			selectOption.setAttributeNode(document.createAttribute('hidden')); // hide from select
		}

		// Add elements
		document.getElementById('group_select_' + membersType).add(selectOption);
		document.getElementById('group_list_' + membersType).appendChild(memberListItem);
	}
}

document.addEventListener("DOMContentLoaded", function(){
	['species', 'individuals'].forEach(function(membersType){
		if (document.getElementById('id_subject_' + membersType)){
			initGroupMembersDisplay(membersType);
		}
	});
});
//----------------------------------------------------------------------------------------------------------------------

// Attribute Categories Formset-----------------------------------------------------------------------------------------
function updateOrderFields(){
	// Find each ORDER form field and number them sequentially from 1 in the order they appear in the DOM
	let currentPosition = 1;
	$.each($('input[id$=-ORDER]'), function(i, val){
    	val.value = currentPosition;
    	currentPosition += 1;
    });
}

function moveCategoryForm(formIndex, direction){
	// Move forms in front-end
	let form1Id = '#form_fields_slot_' + formIndex;
	let form2Id = '#form_fields_slot_' + (formIndex + direction);

	tmpForm1HTML = $(form1Id).html();
	$(form1Id).html($(form2Id).html());
	$(form2Id).html(tmpForm1HTML);

	updateOrderFields();
}

function decreaseCategoryPosition(formIndex){
	if (formIndex > 0){
		moveCategoryForm(formIndex, -1);
	}
}

function increaseCategoryPosition(formIndex){
	if (formIndex + 1 < $('#id_form-TOTAL_FORMS').val()){
		moveCategoryForm(formIndex, +1);
	}
}

function addCategoryForm(){
	numForms = parseInt($('#id_form-TOTAL_FORMS').val());

	newFormHTML = $('#EMPTY_FORM_TEMPLATE').html().replaceAll('__prefix__', numForms);

	$('#down_button_' + (numForms - 1)).prop('hidden', false);
	$('#attribute_categories_html_form_submit_btn').before(newFormHTML);

	// If this is the first form to be added, hide the up button
	if ($('#id_form-TOTAL_FORMS').val() == 0){
		$('#up_button_' + numForms).prop('hidden', true);
	}

	// Hide 'no categories yet' warning
	$('#no_attribute_categories_warning').prop('hidden', true);

	// Increment form count
	$('#id_form-TOTAL_FORMS').val(numForms + 1);
}
//----------------------------------------------------------------------------------------------------------------------
// Ticket Page----------------------------------------------------------------------------------------------------------
function setUserWatcherStatus(addAsWatcher){
	formData = new FormData();
	formData.append('set_watcher_status', addAsWatcher);
	$.ajax({
		type: 'POST',
		url: document.URL,
		data: formData,
		processData: false,
		contentType: false,
		success: function(response){
			buttonSelector = $('#add_as_watcher_btn');
			iconSelector = $('svg', buttonSelector);
			if (response['user_is_watcher']){
				iconSelector.attr({'stroke': 'var(--colorPrimary)'});
			} else {
				iconSelector.attr({'stroke': 'var(--colorForeground)'});
			}
			// Hide tooltip
			buttonSelector.attr({'data-original-title': ''});
		},
	});
}
//----------------------------------------------------------------------------------------------------------------------
