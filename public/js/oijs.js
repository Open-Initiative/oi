function OIajaxCall(url, params, divid) {
    xmlhttp = new XMLHttpRequest();
    if(params==null) {
        method="GET";
    } else {
        method="POST";
    }
    xmlhttp.open(method,url,false);
    xmlhttp.send(params);
    document.getElementById(divid).innerHTML=xmlhttp.responseText;
}
function getValue(eltid){
    elt = document.getElementById(eltid);
    if(elt==null) return null;
    return elt.value.replace(/%/g,"%25").replace(/&/g,"%26").replace(/;/g,"%3B");
}
function newDiv(parentid) {
    divid = "oi"+((new Date).getTime());
    document.getElementById(parentid).innerHTML+='<div id="'+divid+'"></div>';
    return divid;
}

function uploadFile(field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({file:'/message/uploadForm', width:300,height:200,close_previous:"no",popup_css:false,inline:"yes"},
    {window : win,input : field_name});
}

function expandCateg(img, categid){
    if(img.down != 1){
        img.down = 1;
        img.src = "/img/fleche2.png";
        OIajaxCall("/message/listcategories/"+categid, null, "subcateg"+categid);
    } else {
        img.down = null;
        img.src = "/img/fleche1.png";
        document.getElementById("subcateg"+categid).innerHTML = "";
    }
}
function toggle(img, divid) {
    div = document.getElementById(divid);
    if(img.down != 1) {
        img.down = 1;
        img.src = "/img/fleche2.png";
        div.style.display = "block"
    } else {
        img.down = null;
        img.src = "/img/fleche1.png";
        div.style.display = "none"
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
function selectCateg(span, categid) {
    selectedcateg[categid] = !selectedcateg[categid];
    span.className = selectedcateg[categid]?"selectedfilter clickable":"clickable";
    expandCateg(document.getElementById("arrow"+categid), categid);
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
		mode : "textareas",
		theme : "advanced",
		content_css : "/css/tinymce.css",
		plugins : "advlink,emotions,iespell,inlinepopups,media,searchreplace,print,contextmenu,paste,noneditable,nonbreaking,xhtmlxtras,advlist,autosave",

		// Theme options
		theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontselect,fontsizeselect",
		theme_advanced_buttons2 : "cut,copy,paste,search,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,|,forecolor,backcolor",
		theme_advanced_buttons3 : "hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,|,print,|,del,ins,restoredraft",
		theme_advanced_toolbar_location : "top",
		theme_advanced_toolbar_align : "left",
		
		file_browser_callback : 'uploadFile'}
);
