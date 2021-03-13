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
