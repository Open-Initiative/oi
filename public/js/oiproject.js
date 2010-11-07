function addTask(projectid,userid) {
    url = "/project/save/0";
    params = "title="+getValue("newtask_title_"+projectid)+"&assignee="+userid+"&progress=0&inline=1&parent="+projectid;
    divid = newDiv("tasks_"+projectid);
    OIajaxCall(url, params, divid);
}
function finishProject(projectid) {
    OIajaxCall("/project/finish/"+projectid, null, "output");
}
function addSpec(projectid, specorder) {
    if(specorder==-1) divid = newDiv("specs_"+projectid);
    else divid = newDiv("specs_"+projectid+"_"+specorder);
    OIajaxCall("/project/"+projectid+"/editspec/0?divid="+divid+"&specorder="+specorder, null, divid);
    changeSpecType(divid);
}
function editSpec(projectid, specid) {
    divid = "spec_"+projectid+"_"+specid;
    OIajaxCall("/project/"+projectid+"/editspec/"+specid+"?divid="+divid, null, divid);
    changeSpecType(divid);
}
function changeSpecType(divid){
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    type=getValue("type_"+divid);
    projectid=getValue("projectid_"+divid);
    specid=getValue("specid_"+divid);
    url = "/project/"+projectid+"/editspecdetails/"+specid+"?divid="+divid+"&type="+type;
    OIajaxCall(url, null, "spec_"+divid);
    tinyMCE.execCommand('mceAddControl', false, 'text_'+divid);
}
function saveSpec(divid, projectid, order, specid){
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    params = "text="+getValue("text_"+divid)+"&order="+order+"&type="+getValue("type_"+divid);
    if(getValue("url_"+divid)) params+="&url="+getValue("url_"+divid);
    if(getValue("filename_"+divid)) params+="&filename="+getValue("filename_"+divid);
    if(getValue("ts_"+divid)) params+="&ts="+getValue("ts_"+divid);
    if(getValue("image_"+divid)) params+="&image="+getValue("image_"+divid);
    OIajaxCall("/project/"+projectid+"/savespec/"+specid, params, divid);
}
function deleteSpec(projectid, specid) {
    OIajaxCall("/project/"+projectid+"/deletespec/"+specid, null, "output");
    document.getElementById("spec_"+projectid+"_"+specid).innerHTML="";
}
function deltmp(projectid,filename,ts,divid) {
    OIajaxCall("/project/"+projectid+"/deltmp", "filename="+filename+"&ts="+ts+"&divid="+divid, "output");
    changeFile(divid);
}
function changeFile(divid) {
    document.getElementById("filediv_"+divid).style.display="inline";
    document.getElementById("filespan_"+divid).style.display="none";
}
