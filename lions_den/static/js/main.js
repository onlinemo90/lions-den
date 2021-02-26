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

// Load Bootstrap Toasts------------------------------------------------------------------------------------------------
window.addEventListener('load', function () {
	$('.toast').toast('show');
	$(document).ready(function(){
		$('[data-toggle="tooltip"]').tooltip();
	});
});
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

window.addEventListener('load', function () {
	if (document.getElementById("id_subject_image")){
	setDynamicBlobDisplay("id_subject_image_display", "id_subject_image");
	}

	if (document.getElementById("id_subject_audio")){
		setDynamicBlobDisplay("id_subject_audio_display", "id_subject_audio", "id_audio_control");
	}
});
//----------------------------------------------------------------------------------------------------------------------

// Filtering Individuals List by Species--------------------------------------------------------------------------------
window.addEventListener('load', function () {
	if (document.getElementById('select_species')){
		$('#select_species').on('change', function(){
			$.ajax({
				type: 'GET',
				url: document.URL,
				data: 'species_id=' + $(this).val(),
				success: function (response) {
					$('#subject-table').replaceWith(response);
				}
			});
		});
	}
});
//----------------------------------------------------------------------------------------------------------------------

// Group Page - Show and Edit Members-----------------------------------------------------------------------------------
function queryGroupMembers(membersType, id, isDelete){
	let httpMethod, requestData;
	if (id){
		let action = 'add';
		if (isDelete){
			action = 'delete';
		}
		httpMethod = 'POST';
		requestData = {
			'members_type': membersType,
			'id': id,
			'action': action
		}
	} else {
		httpMethod = 'GET';
		requestData = 'members_type=' + membersType;
	}

	$.ajax({
		type: httpMethod,
		url: document.URL,
		data: requestData,
		success: function (response) {
			document.getElementById('group_members_' + membersType).innerHTML = response;
		}
	});
}

function addMemberToGroup(membersType){
	memberId = document.getElementById('group_' + membersType + '_select').value;
	if (memberId){
		return queryGroupMembers(membersType, memberId, false);
	}
}

function deleteMemberFromGroup(membersType, memberId){
	return queryGroupMembers(membersType, memberId, true);
}
//----------------------------------------------------------------------------------------------------------------------

