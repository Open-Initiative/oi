function expandMessage(msgid, depth) {
    if(document.getElementById("message_"+msgid+"_box").expanded != 1)
        OIajaxCall("/message/get/"+msgid+"?mode=ajax&depth="+depth, null, "message_"+msgid+"_box");
    document.getElementById("message_"+msgid+"_box").expanded=1;
    document.getElementById("message_"+msgid+"_box").style.top="-70px";
}
function shrinkMessage(msgid, depth) {
    OIajaxCall("/message/get/"+msgid+"?mode=small&depth="+depth, null, "message_"+msgid+"_box");
    document.getElementById("message_"+msgid+"_box").expanded=0;
    document.getElementById("message_"+msgid+"_box").style.top="0";
}
function addMessage(parentid) {
    if(parentid==null) {
        if(getSelectedCategs(selectedcateg)=="") {
            alert("Sélectionnez une catégorie");
            return;
        }
        location = "/message/new?categs="+getSelectedCategs(selectedcateg);
    } else {
        divid = newDiv("children_"+parentid);
        url = "/message/edit/0?divid="+divid+"&parents="+parentid;
    }
    OIajaxCall(url, null, divid);
    tinyMCE.execCommand('mceAddControl', false, "text_"+divid);
    tinyMCE.execCommand('mceFocus', false, "text_"+divid);
}
function saveMessage(divid, msgid){
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    parents = getValue("parents_"+divid);
    if(parents=="") parents = getSelectedCategs(selectedcateg);
    params = "message="+getValue("text_"+divid).replace(/\+/gi,"%2B")+"&title="+getValue("title_"+divid).replace(/\+/gi,"%2B")+"&parents="+parents;
    OIajaxCall("/message/save/"+msgid, params, divid);
}
function editMessage(msgid) {
    divid = "message_"+msgid;
    OIajaxCall("/message/edit/"+msgid+"?divid="+divid, null, divid);
    tinyMCE.execCommand('mceAddControl', false, "text_"+divid);
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
    divid = newDiv("newParent");
    OIajaxCall("/message/move/"+msgid+"/"+divid, null, divid);
}
function confirmMoveMessage(msgid, divid) {
    OIajaxCall("/message/confirmmove/"+msgid, "parentid="+getValue("parentid_"+divid), "output");
}
function orphanMessage(msgid, parentid) {
    OIajaxCall("/message/orphan/"+msgid, "parentid="+parentid, "output");    
    clearDiv("path_"+parentid);
}
function deleteMessage(msgid) {
    if(confirm("Etes vous sûr de vouloir supprimer définitivement ce message ?")) {
        OIajaxCall("/message/delete/"+msgid, null, "output");
        clearDiv("message_"+msgid);
    }
}
function vote(msgid, opinion){
    OIajaxCall("/message/vote/"+msgid, "opinion="+opinion, "output");
}
