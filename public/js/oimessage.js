function expandMessage(msgid, depth) {
    if(document.getElementById("message_"+msgid).expanded != 1)
        OIajaxCall("/message/get/"+msgid+"?mode=ajax&depth="+depth, null, "message_"+msgid);
    document.getElementById("message_"+msgid).expanded=1;
}
function addMessage(parentid) {
    if(parentid==null) {
        divid = 
        url = "/message/edit/0?divid="+divid;
    } else {
        divid = newDiv("children_"+parentid);
        url = "/message/edit/0?divid="+divid+"&parents="+parentid;
    }
    OIajaxCall(url, null, divid);
    tinyMCE.execCommand('mceAddControl', false, "text_"+divid);
}
function getSelectedCategs(categArray) {
    categlist=[];
    for(categ in categArray) if(categArray[categ]) categlist.push(categ);
    return categlist.join(',');
}
function saveMessage(divid, msgid){
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    parents = getValue("parents_"+divid);
    if(parents=="") parents = getSelectedCategs(selectedcateg);
    params = "message="+getValue("text_"+divid)+"&title="+getValue("title_"+divid)+"&parents="+parents;
    OIajaxCall("/message/save/"+msgid, params, divid);
}
function editMessage(msgid) {
    divid = "message_"+msgid;
    OIajaxCall("/message/edit/"+msgid+"?divid="+divid, null, divid);
    tinyMCE.execCommand('mceAddControl', false, "text_"+divid);
}
function deleteMessage(msgid) {
    OIajaxCall("/message/delete/"+msgid, null, "output");
    document.getElementById("message_"+msgid).innerHTML="";
}
function vote(msgid, opinion){
    OIajaxCall("/message/vote/"+msgid, "opinion="+opinion, "output");
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

selectedcateg = new Array();
function selectCateg(span, categid) {
    selectedcateg[categid] = !selectedcateg[categid];
    span.className = selectedcateg[categid]?"selectedcateg":"";
    if(document.getElementById("messages"))
        OIajaxCall("/message/getall?categs="+getSelectedCategs(selectedcateg), null, "messages");
}
