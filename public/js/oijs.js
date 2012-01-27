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

function OIajaxCall(url, params, divid) {
    xmlhttp = new XMLHttpRequest();
    if(params==null) {
        method="GET";
    } else {
        method="POST";
    }
    xmlhttp.open(method, url, false);
    xmlhttp.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    xmlhttp.send(params);
    if(xmlhttp.status == 531){
        document.getElementById("output").innerHTML = 'ERROR : ' + xmlhttp.responseText;
        return;
    }
    if(xmlhttp.status >= 500){
        document.getElementById("output").innerHTML = 'ERROR : ' +gettext('Unkown server error');
        return;
    }
    if(xmlhttp.status >= 404){
        document.getElementById("output").innerHTML = 'ERROR : ' +gettext('Could not find object');
        return;
    }
    if(xmlhttp.status == 332) document.location.reload();
    if(xmlhttp.status == 333) document.location = xmlhttp.responseText;
    else {
        if(!divid) return xmlhttp.responseText;
        document.getElementById(divid).innerHTML = xmlhttp.responseText;
    }
}
function getValue(eltid, erase){
    elt = document.getElementById(eltid);
    if(elt==null) return null;
    value = elt.value.replace(/%/g,"%25").replace(/&/g,"%26").replace(/;/g,"%3B");
    if(erase) elt.value = "";
    return value;
}
function newDiv(parentid) {
    divid = "oi" + (""+Math.random()).slice(5);
//    document.getElementById(parentid).innerHTML+='<div id="'+divid+'"></div>';
    var newdiv = document.createElement('div');
    newdiv.setAttribute('id',divid);
    document.getElementById(parentid).appendChild(newdiv);
    return divid;
}
function newDivTop(parentid) {
    divid = "oi" + (""+Math.random()).slice(5);
    document.getElementById(parentid).innerHTML='<div id="'+divid+'"></div>' + document.getElementById(parentid).innerHTML;
    return divid;
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

function parseDate(dateString) {
    if(dateString) {
        date = dateString.split(" ")[0].split("-");
        return new Date(parseInt(date[0]), parseInt(date[1]) - 1, parseInt(date[2]));
    }
}

function toggle(img, divid) {
    div = document.getElementById(divid);
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
    form = document.forms[formid];
    params=[];
    for(i=0;i<form.elements.length;i++)
        if(form.elements[i].type=="checkbox")
            params.push(form.elements[i].name+"="+form.elements[i].checked);
        else
            params.push(form.elements[i].name+"="+form.elements[i].value);
    return params.join('&');
}

function uploadFile(field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({file:'/message/uploadForm', width:300,height:200,close_previous:"no",popup_css:false,inline:"yes"},
    {window : win,input : field_name});
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
    categlist=[];
    for(categ in categArray) if(categArray[categ]) categlist.push(categ);
    return categlist.join(',');
}
function applyFilter() {
    categlist = getSelectedCategs(selectedcateg);
    
    paramList = new Array();
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
        anclist = OIajaxCall("/message/listancestors/"+categid, null, null).split(",")
        for(i=0;i<anclist.length;i++) {
            img = document.getElementById("arrow"+anclist[i])
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
        theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontselect,fontsizeselect",
        theme_advanced_buttons2 : "cut,copy,paste,search,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,|,forecolor,backcolor",
        theme_advanced_buttons3 : "hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,|,print,|,del,ins,restoredraft",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        
        file_browser_callback : 'uploadFile'}
);


//IE compatibility
if (!Array.prototype.indexOf)
{
  Array.prototype.indexOf = function(elt /*, from*/)
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

