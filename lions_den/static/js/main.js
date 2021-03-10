// Load Bootstrap Toasts------------------------------------------------------------------------------------------------
$('.toast').toast('show');
$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip();
});
//----------------------------------------------------------------------------------------------------------------------

// Allow Ajax to submit POST forms--------------------------------------------------------------------------------------
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
function getModal(modalID){
	$.ajax({
		type: 'GET',
		url: document.URL,
		data: modalID,
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

function submitModalForm(updateTargetID){
	/*
		Submits the unique modal form
		updateTargetID - ID of the HTML element that the AJAX response is supposed to replace
		If updateTargetID is not provided, then the whole page is reloaded from the server
	*/
	$.ajax({
		type: 'POST',
		url: document.URL,
		data: new FormData(document.getElementById('modalForm')),
        processData: false,
        contentType: false,
		success: function (response) {
			if (updateTargetID){
				$('#' + updateTargetID).replaceWith(response);
			} else {
				location.reload();
			}
		}
	});
}
//----------------------------------------------------------------------------------------------------------------------

// Dynamic image & audio updating in subject forms----------------------------------------------------------------------
function setDynamicBlobDisplay(displayID, widgetID, audioControlID) {
	let reloadAudio = function(){ if (audioControlID){ $("#" + audioControlID)[0].load() } };
	var initialValue = document.getElementById(displayID).src;
	document.querySelector('#' + widgetID).addEventListener('change', function() {
		var file = document.getElementById(widgetID).files[0];
		var displayElement = document.getElementById(displayID);
		if (file){
			var reader  = new FileReader();
			reader.onload = function(e) {
				displayElement.src = e.target.result;
				reloadAudio();
			};
			reader.readAsDataURL(file);
		} else {
			displayElement.src = initialValue;
			reloadAudio();
		}
	});
};

function initDynamicBlobFieldDisplay(){
	if (document.getElementById("id_subject_image")){
		setDynamicBlobDisplay("id_subject_image_display", "id_subject_image");
	}

	if (document.getElementById("id_subject_audio")){
		setDynamicBlobDisplay("id_subject_audio_display", "id_subject_audio", "id_audio_control");
	}
}

document.addEventListener("DOMContentLoaded", function(){
	initDynamicBlobFieldDisplay();
});
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
	$('#attribute_categories_html_form button[type="submit"]').before(newFormHTML);

	// Increment form count
	$('#id_form-TOTAL_FORMS').val(numForms + 1);
}
//----------------------------------------------------------------------------------------------------------------------
