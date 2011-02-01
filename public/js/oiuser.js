function editDetail(type, divid, id) {
    if(!divid) divid = newDiv(type);
    if(!id) id=0;
    
    OIajaxCall("/user/editdetail/"+id+"?divid="+divid+"&type="+type, null, divid);
    new JsDatePick({useMode:2,target:"id_"+divid+"-begining",dateFormat:"%Y-%m-%d"});
    new JsDatePick({useMode:2,target:"id_"+divid+"-end",dateFormat:"%Y-%m-%d"});
    document.getElementById(divid).scrollIntoView();
}
function saveDetail(divid, id) {
    OIajaxCall("/user/savedetail/"+id, prepareForm("form_"+divid), divid);
}
function editTitle() {
    OIajaxCall("/user/edittitle", null, "usertitle");
}
function resetTitle(title) {
    document.getElementById("usertitle").innerHTML = title + '<img class="clickable" src="/img/icons/edit.png" onclick="editTitle()" />';
}
function setUserTitle() {
    title = getValue("select_title");
    OIajaxCall("/user/setusertitle","title=" + title, "output");
    resetTitle(title);
}
function setBirthdate(date) {
    OIajaxCall("/user/setbirthdate", "date="+date.dateFormat("Y-m-d"), "output");
}
function deleteDetail(id, type) {
    OIajaxCall("/user/deletedetail/"+id, "type="+type, "output");
    clearDiv(type+"_"+id);
}
function addContact(userid) {
    OIajaxCall("/user/invite/"+userid, null, "output");
}
function writeMP(userid) {
    OIajaxCall("/user/writemp/"+userid, null, "sendmp");
    show("sendmp");
}
function sendMP(userid) {
    OIajaxCall("/user/sendmp/"+userid, "message="+getValue("MPmessage")+"&subject="+getValue("MPsubject"), "output");
    hide("sendmp");
}
