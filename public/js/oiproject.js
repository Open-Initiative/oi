function addTask(projectid) {
    divid = newDiv("tasks_"+projectid);
    url = "/project/save/0"+projectid;
    params = "title="+getValue("newtask_title_"+projectid)+"&parent="+projectid;
    OIajaxCall(url, params, divid);
}
function addSpec(projectid, specorder) {
    if(specorder==-1) divid = newDiv("specs_"+projectid);
    else divid = newDiv("specs_"+projectid+"_"+specorder);
    url = "/project/"+projectid+"/editspec/0?divid="+divid+"&specorder="+specorder;
    OIajaxCall(url, null, divid);
    changeSpecType(divid);
}
function changeSpecType(divid){
    type=getValue("type_"+divid);
    projectid=getValue("projectid_"+divid);
    url = "/project/"+projectid+"/editspecdetails/0?divid="+divid+"&type="+type;
    OIajaxCall(url, null, "spec_"+divid);
}
function saveSpec(divid, projectid, order, specid){
    params = "text="+getValue("text_"+divid)+"&order="+order+"&type="+getValue("type_"+divid);
    if(getValue("url_"+divid)) params+="&url="+getValue("url_"+divid);
    if(getValue("filename_"+divid)) params+="&filename="+getValue("filename_"+divid);
    if(getValue("image_"+divid)) params+="&image="+getValue("image_"+divid);
    OIajaxCall("/project/"+projectid+"/savespec/"+specid, params, divid);
}
function deleteSpec(projectid, specid) {
    OIajaxCall("/project/"+projectid+"/deletespec/"+specid, null, "output");
    document.getElementById("spec_"+projectid+"_"+specid).innerHTML="";
}