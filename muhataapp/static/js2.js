var wholeList,
    filteredList,
    tags = [],
    selected = -1,
    selected_tags = [];

$(document).ready(function()
{
    $("#search-box").bind('keyup',
        function(event) {

            filterWholeList($(this).val());
            addSuggestionAndEffect();

            // if there is nothing in the searchbar - hide list; otherwise - show it.
            if ( $(this).val() == "" )  $("#suggestionsList").hide();
            else                        $("#suggestionsList").show();

            var ch = event.which;

            // key "down"
            if (ch == 40) {
                if (selected == -1) {
                    selected = 0;
                }else if ( selected == filteredList.length -1 ) {
                    selected = 0;
                }else {
                    selected += 1;
                }
            }
            // key "up"
            else if (ch == 38){
                if (selected == -1 || selected == 0) {
                    selected = filteredList.length -1;
                }else if ( selected == filteredList.length -1 ) {
                    selected -= 1;
                }else {
                    selected -= 1;
                }
            }
            // key "enter"
            else if (ch == 13) {
                if (selected != -1) {
                    add_tag( filteredList[selected] );
                    change_wrapper_position();
                    $("#suggestionsList").hide();
                    $(this).val("");
                    selected = -1;
                }else if ( selected_tags.length != 0 ) {
                    get_selected_tags_as_string_and_submit();
                }
            }
            // clear "selected" as some other key was pressed
            else {
                selected = -1;
            }
            makeChange();
        }
    );

    $("#login-register-link").click(function() {
        $("#login-register").show();
        $("#login-register-wrapper").show();
    });

    $("#login-register-wrapper").click(function() {
        $("#login-register").hide();
        $("#login-register-wrapper").hide();
    });

    $("#login-register-wrapper").hide();
    $("#login-register").hide();

    $('#search-button').attr("disabled", "disabled");

    $('#search-button').click( function () {
        get_selected_tags_as_string_and_submit();
    });

    $('#delete-pic').click( function() {
		var id= $(this).attr("name");

    	$.ajax({
        	url: "/delete-pic/" + id + "/",
        	dataType: "text",
        	success: function() {
				$('#ad-picture-big').hide();
				$('#delete-pic').hide();
				$('#pic-container').html('<input type="file" name="picture" id="id_picture" />');
			}
    	});
	});

    $("#flash-message").fadeOut(4000);

	attach_events_to_input_fields_show_hide_default_text("#id_title", "Заглавие" );
	attach_events_to_input_fields_show_hide_default_text("#id_content", "съдържание на обявата" );
	attach_events_to_input_fields_show_hide_default_text("#id_tags", "тагове" );

	attach_events_to_input_fields_show_hide_default_text("#search-box", "Търси по тагове" );

	attach_events_to_input_fields_show_hide_default_text("#login_username_field", "потребителско име" );
	attach_events_to_input_fields_show_hide_default_text("#login_password_field", "парола" );
	attach_events_to_input_fields_show_hide_default_text("#register_username_field", "потребителско име" );
	attach_events_to_input_fields_show_hide_default_text("#register_password_field", "парола" );
	attach_events_to_input_fields_show_hide_default_text("#register_email_field", "поща" );

	// We must load the whole list of suggestions on front-page load.
	// (it is the front page if there is such an element as 'search-box')
	if ( $("#search-box").length ) {
    	$.ajax({
        	url: "/get-suggestions/",
        	dataType: "text",
        	success: function(data) {
            	wholeList = data.split(" ");}
    	});
	}

}); // end of $(document).ready

function attach_events_to_input_fields_show_hide_default_text(id, text_of_field ) {
	$(id).focus( {text: text_of_field }, default_text_hide ).blur( { text: text_of_field }, default_text_show );
}

// on FOCUS - hides the default text.
function default_text_hide(event) {
	if ( $(this).val() == event.data.text ) {
		$(this).val("")
	}
    $(this).css("color","black");
}
// BLUR - shows the default text.
function default_text_show(event) {
	if ( $(this).val() == "" ) {
		$(this).val(event.data.text);
        $(this).css("color","#aaa");
	}
}


// attach event handlers to all "report" buttons:
$(document).on('click', '.ad-report', report_handler);

function report_handler() {

    var id = $(this).attr("id");

    $(this).html("Сигурни? <a id='report-yes-"+ id +"'>Да</a> | <a id='report-no-"+ id +"'>Не</a>");

    $("#report-yes-"+id).click( function() {
       $.ajax({
        	url: "/report-ad/"+id+"/",
            dataType: "text",
        	success: function() {
            	$("#"+id).html("Обявата е докладвана. Благодарим ви!");
            	}
    		});
	});

    $("#report-no-"+id).click( function() {
      	$("#"+id).html("докладвай");
	});
}

function get_selected_tags_as_string_and_submit() {
    var dataString = "";
    for(var i = 0; i < selected_tags.length; i+= 1) {
        dataString += selected_tags[i] + " ";
    }
    dataString.slice(0,-1);
    $('#hidden-field').val( dataString );
    $("#search-by-tags").submit();
}

// colour an item of the list gray when the user hovers with the mouse or
// uses the arrow keys to navigate over the list.
function makeChange() {
    for(var i = 0; i < filteredList.length; i+= 1) {
        if ( i != selected ) {
             $("#suggestionsList").find("#item-" + i).removeClass("hover");
        } else {
             $("#suggestionsList").find("#item-" + i).addClass("hover");
        }
    }
}

function addSuggestionAndEffect() {
    $("#suggestionsList").empty();
    for (var i = 0; i < filteredList.length; i++) {
        $('#suggestionsList').append('<li id = "item-' + i + '">' + filteredList[i] + '</li>');
    }
    $("#suggestionsList li").mouseenter(
        function() {
            $(this).addClass("hover");
        }).mouseleave(
        function() {
            $(this).removeClass("hover");
        });
    $("#suggestionsList li").click(
        function() {
            add_tag( $(this).get(0).innerText );
            change_wrapper_position();
            $("#suggestionsList").hide();
            $("#search-box").val("").focus();
            selected = -1;
        }
    );
}

function add_tag(tag_name) {
    $("#search-button").removeAttr("disabled");
    $('#tagList').append('<li class = "selected-tags" id = "l' + tag_name + '">' + tag_name +
        ' <span class = "delete-tag" id = "s' + tag_name +
        '" title = "премахни този таг">X</span></li>');
    selected_tags.push(tag_name);
    console.log(selected_tags);

    // the only way to remove a tag from this list is to click the 'X'.
    // Let's attach the event for removing the tag to the 'X':
    $("#s" + tag_name ).click(function () {
        $("#l" + tag_name).remove();
        // add tag to the end of whole list
        wholeList.push(tag_name);
        selected_tags.splice( $.inArray( tag_name, selected_tags ) ,1);
        console.log(selected_tags);
        // check if there are selected tags, and if not - disable search button
        if ( $('.selected-tags').length === 0 ) $('#search-button').attr("disabled", "disabled");
    });
    // remove from whole list. We don't need it in the suggestions box anymore:
    var tag_index = $.inArray( tag_name, wholeList );
    wholeList.splice( tag_index, 1 );
}

function change_wrapper_position() {
    var current = $("#tagList-wrapper").height();
    $("#tagList-wrapper").css("margin-top", -current-25 );
    console.log(current);
}

// this function produces the filtered list
function filterWholeList(str) {
    var newList = [];
    for (var i = 0; i < wholeList.length; i++) {
        if ( wholeList[i].indexOf(str) !== -1 )
            newList[newList.length] = wholeList[i];
    }
    filteredList = newList;
}

// From the MDN Doc:
// https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Array/IndexOf#Compatibility
// indexOf is a recent addition to the ECMA-262 standard; as such it may not be
// present in all browsers. You can work around this by inserting the following
// code at the beginning of your scripts, allowing use of indexOf in implementations
// which do not natively support it. This algorithm is exactly the one specified
// in ECMA-262, 5th edition, assuming Object, TypeError, Number, Math.floor,
// Math.abs, and Math.max have their original value.
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (searchElement) {
        "use strict";
        if (this == null) {
            throw new TypeError();
        }
        var t = Object(this);
        var len = t.length >>> 0;
        if (len === 0) {
            return -1;
        }
        var n = 0;
        if (arguments.length > 0) {
            n = Number(arguments[1]);
            if (n != n) { // shortcut for verifying if it's NaN
                n = 0;
            } else if (n != 0 && n != Infinity && n != -Infinity) {
                n = (n > 0 || -1) * Math.floor(Math.abs(n));
            }
        }
        if (n >= len) {
            return -1;
        }
        var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
        for (; k < len; k++) {
            if (k in t && t[k] === searchElement) {
                return k;
            }
        }
        return -1;
    }
}
