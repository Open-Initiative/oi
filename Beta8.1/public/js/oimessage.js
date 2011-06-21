function expandMessage(msgid, depth) {
    if(document.getElementById("message_"+msgid+"_box").expanded != 1)
        OIajaxCall("/message/get/"+msgid+"?mode=ajax&depth="+depth, null, "message_"+msgid+"_box");
    document.getElementById("message_"+msgid+"_box").expanded=1;
}
function shrinkMessage(msgid, depth) {
    OIajaxCall("/message/get/"+msgid+"?mode=small&depth="+depth, null, "message_"+msgid+"_box");
    document.getElementById("message_"+msgid+"_box").expanded=0;
    document.getElementById("message_"+msgid+"_box").style.top="0";
}
function addMessage(parentid) {
    if(parentid==null) {
        location = "/message/new?categs="+getSelectedCategs(selectedcateg);
    } else {
        divid = newDiv("children_"+parentid);
        url = "/message/edit/0?divid="+divid+"&parent="+parentid;
    }
    OIajaxCall(url, null, divid);
    document.getElementById(divid).scrollIntoView();
    tinyMCE.execCommand('mceAddControl', false, "text_"+divid);
    tinyMCE.execCommand('mceFocus', false, "text_"+divid);
}
function saveMessage(divid, msgid){
    parent = getValue("parent_"+divid);
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    params = "message="+getValue("text_"+divid).replace(/\+/gi,"%2B")+"&title="+getValue("title_"+divid).replace(/\+/gi,"%2B")+"&parent="+parent;
    if(document.getElementById("rfp") && document.getElementById("rfp").checked) params +="&rfp=True";
    OIajaxCall("/message/save/"+msgid, params, divid);
}
function cancelMessage(divid, msgid){
    if(msgid==0) {
        if(getValue("parents_"+divid)) clearDiv(divid);
        else document.location = "/";
    }
    else {
        tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
        OIajaxCall("/message/get/"+msgid+"?mode=ajax", null, divid);
    }
}
function editMessage(msgid) {
    divid = "message_"+msgid;
    OIajaxCall("/message/edit/"+msgid+"?divid="+divid, null, divid);
    tinyMCE.execCommand('mceAddControl', false, "text_"+divid);
}
function editMessageTitle(divid, title) {
    document.getElementById("msgtitle_"+divid).innerHTML = '<input id="title_'+divid+'" class="msgfield" type="text" value="'+title+'"/>';
}
function hideMessage(msgid) {
    OIajaxCall("/message/hide/"+msgid, null, "output");
}
function shareMessage(msgid) {
    divid = newDiv("msgdialogue_"+msgid);
    OIajaxCall("/message/share/"+msgid+"/"+divid, null, divid);
}
function confirmShareMessage(msgid, divid) {
    OIajaxCall("/message/confirmshare/"+msgid, "username="+getValue("usershare_"+divid), "output");
}
function moveMessage(msgid) {
    OIajaxCall("/message/move/"+msgid+"/path_"+msgid, null, "path_"+msgid);
}
function confirmMoveMessage(msgid, divid) {
    OIajaxCall("/message/confirmmove/"+msgid, "parentid="+getValue("parentid_"+divid), "output");
}
function orphanMessage(msgid, parentid) {
    OIajaxCall("/message/orphan/"+msgid, "parentid="+parentid, "output");    
    clearDiv("path_"+parentid);
}
function deleteMessage(msgid) {
    if(confirm(gettext("Are you sure you want to delete this message permanently?"))) {
        OIajaxCall("/message/delete/"+msgid, null, "output");
        clearDiv("message_"+msgid);
    }
}
function vote(msgid, opinion){
    OIajaxCall("/message/vote/"+msgid, "opinion="+opinion, "output");
}
function observeMessage(msgid, param){
    OIajaxCall("/message/observe/"+msgid, param, "output");
}
