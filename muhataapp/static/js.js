// Normalizing functions for event hadlers are taken
// from http://eloquentjavascript.net/chapter13.html
// The comments are mine.

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

// The following 2 functions are needed because of the different syntax
// between IE and other browsers for the EventListener function. This is
// safer than "browser sniffing" because it will still work if IE decides
// to switch to the standarts in the future.
function registerEventHandler(node, event, handler) {
    if (typeof node.addEventListener == "function")
        node.addEventListener(event, handler, false);
    else
        node.attachEvent("on" + event, handler);
}

function unregisterEventHandler(node, event, handler) {
    if (typeof node.removeEventListener == "function")
        node.removeEventListener(event, handler, false);
    else
        node.detachEvent("on" + event, handler);
}

// Different browsers return different methods and also return different
// char codes. This function deals with this fact.
function normaliseKeyStrokes(event) {
    if (event.type == "keyup") {

        if (event.charCode === 0 || event.charCode == undefined) {
            event.character = String.fromCharCode(event.keyCode);
        }
        else {
            event.character = String.fromCharCode(event.charCode);
        }
    }

    return event;
}

//
function addHandler(node, type, handler) {

    function wrapHandler(event) {
        handler(normaliseKeyStrokes(event || window.event));
    }

    registerEventHandler(node, type, wrapHandler);

    return {node: node, type: type, handler: wrapHandler};
}

// Untill now, we were dealing with normalization.
// This function returns the AJAX object. It uses exception handlers,
// which are needed anyway with the
function makeHttpObject() {
    try { return new XMLHttpRequest(); }
    catch (error) {}
    try { return new ActiveXObject("Msxml2.XMLHTTP"); }
    catch (error) {}
    try { return new ActiveXObject("Microsoft.XMLHTTP"); }
    catch (error) {}

    throw new Error("Could not create HTTP request object.");
}

function displayTopResults() {
    request.open("GET", "/get-suggestions/", true);
    request.send(null);
    suggestions.style.visibility = "visible";
}

function hideResults() {
    suggestions.style.visibility = "hidden";
}

function filterSuggestions(str) {
    var newSuggestions = [];
    for (var i = 0; i < suggestionsList.length; i++) {
        if ( suggestionsList[i].indexOf(str) !== -1 )
            newSuggestions[newSuggestions.length] = suggestionsList[i];
    }
    suggestionsList = newSuggestions;
    data.innerHTML = suggestionsList;
}

function change(e) {

    ch = event.character;
    console.log(ch);

    filterSuggestions(box.node.value)
    changeSuggestionsBox();

}

// This function "draws" the suggestion box after the list has been altered
// via other functions.
function changeSuggestionsBox() {

    var displayHTML = "<ul id = 'suggestions-list'>";

    for (var i = 0; i < suggestionsList.length; i++) {
        displayHTML += "<li>" + suggestionsList[i] + "</li>";
    }

    displayHTML += "</ul>";
    suggestions.innerHTML = displayHTML;
}

function cev(e) {
    alert(e);
}

var box,
    suggestions,
    data,
    suggestionsList = [],
    wholeList = [],
    request = makeHttpObject();

window.onload = function() {
    box = document.getElementById("search-box");
    suggestions = document.getElementById("suggestionsBox");
    data = document.getElementById("data");

    // on focus - display top suggestions, on blur - hide suggestions
    addHandler(box, "focus", displayTopResults);
    addHandler(box, "blur", hideResults);

    // on key press - change suggestions or add tag if "Enter" is pressed
    box = addHandler(box, "keyup", change);
    // box = addHandler(box, "keyup", changeKU);
}

// when the server comunicates back - send for displaying the changes.
request.onreadystatechange = function() {
    if (request.readyState == 4) {
        if (request.status == 200) {
            wholeList = request.responseText.split(" ");
            suggestionsList = wholeList;
            changeSuggestionsBox();
        }
    }
};

