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
function getSelectedCategs(categArray) {
    categlist=[];
    for(categ in categArray) if(categArray[categ]) categlist.push(categ);
    return categlist.join(',');
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
selectedDateFilter = null;
datemin = null;
datemax = null;
function applyFilter() {
    categlist = getSelectedCategs(selectedcateg)
    
    paramList = new Array();
    if(categlist.length) paramList.push("categs=" + categlist);
    if(datemin) paramList.push("datemin="+datemin.getFullYear()+","+(datemin.getMonth()+1)+","+datemin.getDate());
    if(datemax) paramList.push("datemax="+datemax.getFullYear()+","+(datemax.getMonth()+1)+","+datemax.getDate());
    
    if(document.getElementById("messages"))
        OIajaxCall("/message/getall?"+paramList.join("&"), null, "messages");
}
function selectCateg(span, categid) {
    selectedcateg[categid] = !selectedcateg[categid];
    span.className = selectedcateg[categid]?"selectedcateg clickable":"clickable";
    applyFilter();
}
function setDateDelta(span,delta) {
    if(selectedDateFilter) selectedDateFilter.style.fontWeight="normal";
    selectedDateFilter = span;
    span.style.fontWeight="bold";
    datemax = null;
    datemin = new Date();
    datemin.setDate(datemin.getDate()-delta);
    applyFilter();
}
function setAnyDate(span) {
    if(selectedDateFilter) selectedDateFilter.style.fontWeight="normal";
    selectedDateFilter = span;
    span.style.fontWeight="bold";
    datemax = null;
    datemin = null;
    applyFilter();
}
