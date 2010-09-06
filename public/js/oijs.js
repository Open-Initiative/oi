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

function showcoucou(url) {
    alert("coucou "+url);
}

function uploadFile(field_name, url, type, win) {
    tinyMCE.activeEditor.windowManager.open({file:'/message/uploadForm', width:300,height:200,close_previous:"no",popup_css:false,inline:"yes"},
    {window : win,input : field_name});
}

tinyMCE.init({
		// General options
		mode : "textareas",
		theme : "advanced",
		plugins : "advlink,emotions,iespell,inlinepopups,media,searchreplace,print,contextmenu,paste,noneditable,nonbreaking,xhtmlxtras,advlist,autosave",

		// Theme options
		theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,formatselect,fontselect,fontsizeselect",
		theme_advanced_buttons2 : "cut,copy,paste,search,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,|,forecolor,backcolor",
		theme_advanced_buttons3 : "hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,|,print,|,del,ins,restoredraft",
		theme_advanced_toolbar_location : "top",
		theme_advanced_toolbar_align : "left",
		
		file_browser_callback : 'uploadFile'});
