function expandMessage(msgid, depth) {
    if(document.getElementById("message_"+msgid+"_box").expanded != 1)
        OIajaxCall("/message/get/"+msgid+"?mode=ajax&depth="+depth, null, "message_"+msgid+"_box");
    document.getElementById("message_"+msgid+"_box").expanded=1;
    document.getElementById("message_"+msgid+"_box").style.top="-70px";
}
function addMessage(parentid) {
    if(parentid==null) {
        if(getSelectedCategs(selectedcateg)=="") {
            alert("Sélectionnez une catégorie");
            return;
        }
        divid = "messages";
        url = "/message/edit/0?divid="+divid;
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
function deleteMessage(msgid) {
    OIajaxCall("/message/delete/"+msgid, null, "output");
    document.getElementById("message_"+msgid).innerHTML="";
}
function vote(msgid, opinion){
    OIajaxCall("/message/vote/"+msgid, "opinion="+opinion, "output");
}
