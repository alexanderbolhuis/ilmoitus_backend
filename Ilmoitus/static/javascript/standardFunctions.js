Number.prototype.formatMoney = function(c, d, t){
var n = this, 
    c = isNaN(c = Math.abs(c)) ? 2 : c, 
    d = d == undefined ? "." : d, 
    t = t == undefined ? "," : t, 
    s = n < 0 ? "-" : "", 
    i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", 
    j = (j = i.length) > 3 ? j % 3 : 0;
   return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
 };

function showServerMessage(jqXHR, alternativeMessage, title){
    var actualMessage;
    if(jqXHR.responseJSON && jqXHR.responseJSON.user_message) {
        actualMessage = jqXHR.responseJSON.user_message;
    } else {
        actualMessage = alternativeMessage;
    }
    showMessage(actualMessage, title);
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