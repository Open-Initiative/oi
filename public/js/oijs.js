function trim (myString)
{
    return myString.replace(/^\s+/g,'').replace(/\s+$/g,'')
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function OIajaxCall(url, params, divid, callBack) {
    if(divid) document.getElementById(divid).innerHTML = gettext('loading...');
    var xmlhttp = new XMLHttpRequest();
    if(params==null) {
        method="GET";
    } else {
        method="POST";
    }
    xmlhttp.onreadystatechange=function() {
        if(xmlhttp.readyState < 4) return;
        if(xmlhttp.status == 531)
            document.getElementById("output").innerHTML = gettext('ERROR : ') + xmlhttp.responseText;
        else if(xmlhttp.status >= 500)
            document.getElementById("output").innerHTML = gettext('ERROR : ') +gettext('Unkown server error');
        else if(xmlhttp.status >= 431 || xmlhttp.status == 403)
            document.getElementById("output").innerHTML = gettext('Forbidden : ') + xmlhttp.responseText;
        else if(xmlhttp.status >= 404)
            document.getElementById("output").innerHTML = gettext('ERROR : ') +gettext('Could not find object');
        else if(xmlhttp.status == 332) document.location.reload(true);
        else if(xmlhttp.status == 333) document.location = xmlhttp.responseText;
        else if(xmlhttp.status == 200){
            if(divid)document.getElementById(divid).innerHTML = xmlhttp.responseText;
            if(callBack)callBack(xmlhttp.responseText);
        }
    }
    xmlhttp.open(method, url, true);
    xmlhttp.withCredentials = true;
    xmlhttp.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    xmlhttp.send(params);
}
function makeObjectCallback(method, object) {
    return function() {method.apply(object, arguments)};
}
function randid() {
    return "oi" + (""+Math.random()).slice(5);
}
function getValue(eltid, erase){
    var elt = document.getElementById(eltid);
    if(elt==null) return null;
    var value = encodeURIComponent(elt.value);
    if(erase) elt.value = "";
    return value;
}
function newDiv(parentid) {
    var divid = randid();
    var newdiv = document.createElement('div');
    newdiv.setAttribute('id',divid);
    document.getElementById(parentid).appendChild(newdiv);
    return divid;
}
Date.prototype.add = function add(timedelta) {
    return new Date(this.getTime() + timedelta);
}

function clearDiv(divid) {
    document.getElementById(divid).innerHTML="";
}
function show(divid) {
    document.getElementById(divid).style.display="block";
}
function hide(divid) {
    document.getElementById(divid).style.display="none";
}
function hidePopups() {
    if(document.ignoreClosePopups) {
        document.ignoreClosePopups = false;
        return;
    }
    var i, popup;
    for(popup=document.popups[i=0]; i<document.popups.length; popup=document.popups[++i])
        hide(popup.id);
}
function addPopup(popup) {
    document.popups = (document.popups || []).concat(popup);
    addEvent(document, "click", hidePopups);
}
function parseDate(dateString) {
    if(dateString) {
        var date = dateString.split(" ")[0].split("-");
        return new Date(parseInt(date[0],10), parseInt(date[1],10) - 1, parseInt(date[2],10));
    }
}

function toggle(img, divid) {
    var div = document.getElementById(divid);
    if(document.defaultView.getComputedStyle(div,null).getPropertyValue('display').toString() == "block") {
        if(img){
            img.down = null;
            img.src = "/img/fleche1.png";
        }
        div.style.display = "none"
    } else {
        if(img){
            img.down = 1;
            img.src = "/img/fleche2.png";
        }
        div.style.display = "block"
    }
}

function prepareForm(formid) {
    var form = document.forms[formid];
    params=[];
    for(i=0;i<form.elements.length;i++)
        if(form.elements[i].type=="checkbox")
            params.push(form.elements[i].name+"="+form.elements[i].checked);
        else
            params.push(form.elements[i].name+"="+encodeURIComponent(form.elements[i].value));
    return params.join('&');
}

function uploadFile(field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({file:'/message/uploadForm', width:300,height:200,close_previous:"no",popup_css:false,inline:"yes"},
    {window : win,input : field_name});
}

function slideIndex(nextid) {
    if(!sliding) {
        sliding = true;
        if(nextid) nextSlide = jQuery('#indexslide'+nextid);
        else if(jQuery('.indexslide:visible').nextAll(".indexslide").length) nextSlide = jQuery('.indexslide:visible').nextAll(".indexslide:first");
        else nextSlide = jQuery('.indexslide').first();
        jQuery(".slidertip").fadeOut()
        jQuery('.indexslide:visible').animate({width: "toggle"},1000);
        nextSlide.delay(1000).animate({width: "toggle"},1000).next(".slidertip").delay(1600).fadeIn(1500);
        
        if(nextid) nextIcon = jQuery('#slidericon'+nextid);
        else if(jQuery('.slidericonselected').next().length) nextIcon = jQuery('.slidericonselected').next();
        else nextIcon = jQuery('.slidericon').first();
        jQuery('.slidericonselected').removeClass("slidericonselected");
        nextIcon.addClass("slidericonselected");
        
        if(nextid) nextImg = jQuery('#sliderimg'+nextid);
        else if(jQuery('.sliderimg:visible').next().length) nextImg = jQuery('.sliderimg:visible').next();
        else nextImg = jQuery('.sliderimg').first();
        jQuery('.sliderimg:visible').fadeOut();
        nextImg.delay(1000).fadeIn();
        setTimeout(function(){sliding = false;}, 2000);
        document.getElementById('preslink').hash = '#' + nextSlide.attr('id')[10];
    }
}
function slidePres(id) {
    jQuery('.presslide').slideUp();
    jQuery(id).slideDown();
}

function expandCateg(img, categid, dest){
    if(img.down != 1){
        img.down = 1;
        img.src = "/img/fleche2.png";
        url = "/message/listcategories/"+categid;
        if(dest) url += "?dest="+dest;
        OIajaxCall(url, null, "subcateg"+categid);
    } else {
        img.down = null;
        img.src = "/img/fleche1.png";
        document.getElementById("subcateg"+categid).innerHTML = "";
    }
}

selectedcateg = new Array();
selectedDateFilter = null;
datemin = null;
datemax = null;
selectedStateFilter = null;
state = null;
function getSelectedCategs(categArray) {
    var categlist=[];
    for(categ in categArray) if(categArray[categ]) categlist.push(categ);
    return categlist.join(',');
}
function applyFilter() {
    var categlist = getSelectedCategs(selectedcateg);
    
    var paramList = new Array();
    if(categlist.length) paramList.push("categs=" + categlist);
    if(datemin) paramList.push("datemin="+datemin.getFullYear()+","+(datemin.getMonth()+1)+","+datemin.getDate());
    if(datemax) paramList.push("datemax="+datemax.getFullYear()+","+(datemax.getMonth()+1)+","+datemax.getDate());
    if(state!=null) paramList.push("state="+state);
    
    if(document.getElementById("messages"))
        OIajaxCall("/message/getall?"+paramList.join("&"), null, "messages");
    if(document.getElementById("projects"))
        OIajaxCall("/project/getall?"+paramList.join("&"), null, "projects");
}
function selectCateg(span, categid, dest) {
    if(!span) {
        var anclist = OIajaxCall("/message/listancestors/"+categid, null, null).split(",")
        for(i=0;i<anclist.length;i++) {
            var img = document.getElementById("arrow"+anclist[i])
            expandCateg(img, Number(anclist[i]), null);
        }
        span = document.getElementById("categ_"+categid)
    }
    selectedcateg[categid] = !selectedcateg[categid];
    span.className = selectedcateg[categid]?"selectedfilter clickable":"clickable";
    expandCateg(document.getElementById("arrow"+categid), categid, dest);
    applyFilter();
}
function setDateDelta(span,delta) {
    if(selectedDateFilter) selectedDateFilter.className="";
    selectedDateFilter = span;
    span.className="selectedfilter";
    datemax = null;
    if(delta==null){
        datemin = null;
    }else {
        datemin = new Date();
        datemin.setDate(datemin.getDate()-delta);
    }
    applyFilter();
}
function setPrjState(span,statenum) {
    if(selectedStateFilter) selectedStateFilter.className="";
    selectedStateFilter = span;
    span.className="selectedfilter";
    state = statenum;
    applyFilter();
}

tinyMCE.init({
        // General options
        mode : "specific_textareas",
        editor_deselector : "norich",
        theme : "advanced",
        content_css : "/css/tinymce.css",
        plugins : "advlink,emotions,iespell,inlinepopups,media,searchreplace,print,contextmenu,paste,noneditable,nonbreaking,xhtmlxtras,advlist",

        // Theme options
        theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontselect, bullist,numlist,|,image,|,forecolor,backcolor,|,emotions",
        theme_advanced_buttons2 : "",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        
        file_browser_callback : 'uploadFile'}
);


//IE compatibility
if (!Array.prototype.indexOf)
{
  Array.prototype.indexOf = function indexOf(elt /*, from*/)
  {
    var len = this.length >>> 0;

    var from = Number(arguments[1]) || 0;
    from = (from < 0)
         ? Math.ceil(from)

         : Math.floor(from);
    if (from < 0)
      from += len;

    for (; from < len; from++)
    {
      if (from in this &&
          this[from] === elt)
        return from;
    }
    return -1;
  };
}
if (!Event.prototype.stopPropagation)
    Event.prototype.stopPropagation = function stopPropagation(){this.cancelBubble=true};
function addEvent(obj, evType, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evType, fn, false);
        return true;
    } else if (obj.attachEvent) {
        var r = obj.attachEvent("on" + evType, fn);
        return r;
    } else {
        alert("Handler could not be attached");
    }
}

