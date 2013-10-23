function editDetail(type, divid, id) {
    if(!divid) divid = newDiv(type);
    if(!id) id=0;
    
    OIajaxCall("/user/editdetail/"+id+"?divid="+divid+"&type="+type, null, divid, 
        function(){new JsDatePick({useMode:2,target:"id_"+divid+"-begining",dateFormat:"%Y-%m-%d"});
        new JsDatePick({useMode:2,target:"id_"+divid+"-end",dateFormat:"%Y-%m-%d"});
        document.getElementById(divid).scrollIntoView();});
}
function saveDetail(divid, id) {
    OIajaxCall("/user/savedetail/"+id, prepareForm("form_"+divid), divid);
}
function editBio() {
    jQuery('#bio').hide();
    jQuery('#bio_edit').fadeIn();
    var ed = new tinymce.Editor('bio_textedit', objectInitTinyMce, tinymce.EditorManager);
    ed.render();
}
function saveBio() {
    tinymce.remove('#bio_textedit');
    OIajaxCall("/user/savebio", "bio="+encodeURIComponent(getValue('bio_textedit')), "output", function(){
        jQuery('#bio_edit').hide();
        jQuery('#bio').fadeIn();
        document.getElementById("bio").innerHTML = getValue('bio_textedit');
    });
}
function cancelBio() {
    jQuery('#bio_edit').hide();
    jQuery('#bio').fadeIn();
    tinymce.remove('#bio_textedit');
}
function setRSS(divid, id) {
    OIajaxCall("/user/setrss/", "rss="+getValue("rssfeed"), "output");
}
function editUserTitle() {
    OIajaxCall("/user/edittitle", null, "usertitle");
}
function resetUserTitle(title) {
    document.getElementById("usertitle").innerHTML = title + ' <img class="clickable" src="/img/icons/edit.png" onclick="editUserTitle()" />';
}
function setUserTitle() {
    title = getValue("select_title");
    OIajaxCall("/user/settitle","title=" + title, "output", 
        function(){resetUserTitle(title);});
}
function selectNameDisplay() {
    OIajaxCall("/user/selectnamedisplay", null, "fullname");
}
function resetFullName(fullname) {
    document.getElementById("fullname").innerHTML = fullname + ' <img class="clickable" src="/img/icons/edit.png" onclick="selectNameDisplay()" />';
}
function setNameDisplay() {
    displaytype = getValue("select_display");
    display = document.getElementById("select_display").options[displaytype].innerHTML;
    OIajaxCall("/user/setnamedisplay","display=" + displaytype, "output", 
        function(){resetFullName(display);});
}
function setBirthdate(date) {
    OIajaxCall("/user/setbirthdate", "date="+date.dateFormat("Y-m-d"), "output");
}
function deleteDetail(id, type) {
    OIajaxCall("/user/deletedetail/"+id, "type="+type, "output", 
        function(){clearDiv(type+"_"+id);});
}
function addContact(username) {
    OIajaxCall("/user/invite/"+username, null, "output");
}
function setemailing(label, send) {
    OIajaxCall("/user/setemailing", "label="+label+"&send="+send, "output");
}
function saveName() {
    OIajaxCall("/user/savename", prepareForm("contact_name"), "output", function(){
        document.getElementById("contact_lastname").innerHTML = document.getElementById("contact_lastname_info").value;
        document.getElementById("contact_firstname").innerHTML = document.getElementById("contact_firstname_info").value;
    });
}
function saveContactInfo() {
    OIajaxCall("/user/savecontactinfo", prepareForm("contact_form"), "output", function(){
        var contact = prepareForm("contact_form").split("&");
        for(var i = 0; i < contact.length; i++){
            document.getElementById("contact_"+contact[i].split("=")[0]).innerHTML = decodeURIComponent(contact[i].split("=")[1]);
        }
    });
}
function resetName(){
    document.getElementById("contact_lastname_info").value = "";
    document.getElementById("contact_firstname_info").value = "";
}
function resetContactInfo() {
    var contact = prepareForm("contact_form").split("&");
    for(var i = 0; i < contact.length; i++){
        document.getElementById("id_"+contact[i].split("=")[0]).value = "";
    }
}
function writeMP(username) {
    OIajaxCall("/user/writemp/"+username, null, "sendmp", 
        function(){show("sendmp");});
}
function sendMP(username) {
    tinymce.remove('#MPmessage');
    OIajaxCall("/user/sendmp/"+username, "message="+encodeURIComponent(getValue("MPmessage"))+"&subject="+getValue("MPsubject"), "output",
        function(){hide("sendmp");});
}
function archiveNotice(noticeid) {
    OIajaxCall("/user/archivenotice", "notice="+noticeid, "output", 
        function(){clearDiv("notice_"+noticeid);});
}
function switchPrjList(listid, headid) {
    jQuery(".prjlist").slideUp();
    jQuery("#prjlist"+listid).slideDown();
    if(headid){
        var block_headid = ["listid_1","listid_2","listid_3"];
        for(var i = 0; i < block_headid.length; i++){
            if(headid == block_headid[i]){
                if(document.getElementById(block_headid[i]).style.fontWeight != "bold"){
                    document.getElementById(block_headid[i]).style.fontSize = "16px";
                    document.getElementById(block_headid[i]).style.fontWeight = "bold";
                }
            }else{
                if(document.getElementById(block_headid[i]).style.fontWeight == "bold"){
                    document.getElementById(block_headid[i]).style.fontSize = "14px";
                    document.getElementById(block_headid[i]).style.fontWeight = "";
                }
            }
        }
    }
}
function saveSetting(observerid, use_default, noticeField, send){
    var param = "";
    if(getValue("freq_"+observerid)) param += "&frequency="+getValue("freq_"+observerid);
    if(use_default != null) param += "&use_default="+use_default;
    if(noticeField) param += "&noticeField="+noticeField+"&send="+send;
    OIajaxCall("/notification/settings/"+observerid+"/save", param, "output", 
    function(){
        if(!use_default){
            show("notice_setting_"+observerid);
        }else{
            hide("notice_setting_"+observerid);
        }
    });
}
