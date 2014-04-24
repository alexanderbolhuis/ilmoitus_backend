// Add a row to a table. Is a direct copy of the final row. Execute just before filling in forms in the final row. (onkeydown)
function addTableRow(tableId) {
	var table = $("#"+tableId);
	$("#"+tableId+" tbody tr").last().clone().appendTo("#"+tableId+" tbody").find('input').not(':button').val('');
    $(".datepicker").last().removeAttr("id");
    $(".datepicker").last().removeClass("hasDatepicker");
    $(".datepicker").datepicker();
}

function removeTableRow(tableId, rowIndex) {
	if($("#"+tableId+" tbody tr").length > 1) {
		$("#"+tableId+" tbody tr").eq(rowIndex).remove();
	} else {
		//If only one row left, clear row input fields
        $("#"+tableId+" tbody tr").find('input').not(':button').val('');
	}
}

//An array to support multiple selectable tables on a single page. Key is the table ID. 
var currentlySelected = Array();
function SetTableSelectable(tableId) {
	//Makes it possible to select an item in the table.
    $("#"+tableId+" tbody tr").click(function() {
    	var table = $(this).parent().parent();
        $(currentlySelected[table.attr("id")]).removeClass("selected");
        currentlySelected[table.attr("id")] = this;
        $(this).addClass("selected")
    });
}

function getTableSelectedItem(tableId) {
	if (typeof currentlySelected[tableId].id === 'undefined') {
        return -1;
    } else {
        return currentlySelected[tableId].id;
    }
}

/**
 * Show an error message with the given message and title.
 * 
 * @param {String} message The message the error should show. Can use HTML.
 * @param {String} title Optional. The title of the error message.
 */
function showMessage(message, title) {
    title = (typeof title === "undefined") ? "" : title; //Title is optional.
    $("body").append(
	"<div class='coverBg' onclick='closeMessage();' id='coverBg' ></div>"+
    "<div class='cover' id='messageCover'>" +
        "<div class='header'>" +
            title +
            "<div class='closeButton' onclick='closeMessage();'>X</div>" +
        "</div>" +
        "<div class='contentMessage'>" +
        	message +
        "</div>" +
    "</div>");
    $("#messageCover").fadeIn();
    $("#coverBg").fadeIn();
}

/**
 * Close the error message
 */
function closeMessage() {
	$("#messageCover").fadeOut();
	$("#coverBg").fadeOut();
    setTimeout(function(){
        $("#messageCover").remove();
        $("#coverBg").remove();
    }, 600);
    
}

$(function() {
    $( ".datepicker" ).datepicker();
});