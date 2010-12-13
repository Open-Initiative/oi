function addTask(projectid,userid) {
    url = "/project/save/0";
    params = "title="+getValue("newtask_title_"+projectid)+"&assignee="+userid+"&progress=0&inline=1&parent="+projectid;
    divid = newDiv("tasks_"+projectid);
    OIajaxCall(url, params, divid);
}
function bidProject(projectid) {
    OIajaxCall("/project/bid/"+projectid, null, "output");
}
function startProject(projectid) {
    OIajaxCall("/project/start/"+projectid, null, "output");
}
function deliverProject(projectid) {
    OIajaxCall("/project/deliver/"+projectid, null, "output");
}
function validateProject(projectid) {
    OIajaxCall("/project/validate/"+projectid, null, "output");
}
function evalProject(projectid, rating) {
    OIajaxCall("/project/eval/"+projectid, null, "prjdialogue_"+projectid);
}
function confirmEvalProject(projectid) {
    OIajaxCall("/project/confirmeval/"+projectid, "rating="+getValue("evaluate_"+projectid), "output");
}
function hideProject(projectid) {
    OIajaxCall("/project/hide/"+projectid, null, "output");
}
function shareProject(projectid) {
    divid = newDiv("prjdialogue_"+projectid);
    OIajaxCall("/project/share/"+projectid+"/"+divid, null, divid);
}
function confirmShareProject(projectid, divid) {
    OIajaxCall("/project/confirmshare/"+projectid, "username="+getValue("usershare_"+divid), "output");
}
function deleteProject(projectid) {
    if(confirm("Etes vous sûr de vouloir supprimer définitivement ce projet ?")) {
        OIajaxCall("/project/delete/"+projectid, null, "output");
        clearDiv("spec_"+projectid+"_"+specid);
    }
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
    params = "text="+getValue("text_"+divid).replace(/\+/gi,"%2B")+"&order="+order+"&type="+getValue("type_"+divid);
    if(getValue("url_"+divid)) params+="&url="+getValue("url_"+divid);
    if(getValue("filename_"+divid)) params+="&filename="+getValue("filename_"+divid);
    if(getValue("ts_"+divid)) params+="&ts="+getValue("ts_"+divid);
    if(getValue("image_"+divid)) params+="&image="+getValue("image_"+divid);
    OIajaxCall("/project/"+projectid+"/savespec/"+specid, params, divid);
}
function deleteSpec(projectid, specid) {
    if(confirm("Etes vous sûr de vouloir supprimer définitivement cette spécification ?")) {
        OIajaxCall("/project/"+projectid+"/deletespec/"+specid, null, "output");
        clearDiv("spec_"+projectid+"_"+specid);
    }
}
function deltmp(projectid,filename,ts,divid) {
    if(confirm("Etes vous sûr de vouloir supprimer définitivement cette pièce jointe ?")) {
        OIajaxCall("/project/"+projectid+"/deltmp", "filename="+filename+"&ts="+ts+"&divid="+divid, "output");
        changeFile(divid);
    }
}
function changeFile(divid) {
    document.getElementById("filediv_"+divid).style.display="inline";
    document.getElementById("filespan_"+divid).style.display="none";
}
