function addTask(projectid,userid) {
    url = "/project/save/0";
    params = "title="+getValue("newtask_title_"+projectid)+"&assignee="+userid+"&progress=0&inline=1&parent="+projectid;
    divid = newDiv("tasks_"+projectid);
    OIajaxCall(url, params, divid);
}
function editDate(projectid, field_name, date) {
    OIajaxCall("/project/editdate/"+projectid, "field_name="+field_name+"&date="+date.dateFormat("Y-m-d"), "output");
}
function bidProject(projectid, rating) {
    OIajaxCall("/project/bid/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
}
function confirmBidProject(projectid) {
    OIajaxCall("/project/confirmbid/"+projectid, "bid="+getValue("bid_"+projectid), "output");
    hide("prjdialogue_"+projectid);
}
function assignProject(projectid) {
    OIajaxCall("/project/assign/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
}
function takeonProject(projectid) {
    OIajaxCall("/project/takeon/"+projectid, "offer="+getValue("offer_"+projectid), "output");
    hide("prjdialogue_"+projectid);
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
function setStar(projectid, number) {
    for(i=1;i<=5;i++) 
        if(i<=number) document.getElementById("star"+i+"_"+projectid).src = "/img/icons/staryes.png";
        else document.getElementById("star"+i+"_"+projectid).src = "/img/icons/starno.png";
    document.getElementById("evaluate_"+projectid).value = number;
}
function evalProject(projectid, rating) {
    OIajaxCall("/project/eval/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
}
function confirmEvalProject(projectid) {
    OIajaxCall("/project/confirmeval/"+projectid, "rating="+getValue("evaluate_"+projectid), "output");
    hide("prjdialogue_"+projectid);
}
function hideProject(projectid) {
    OIajaxCall("/project/hide/"+projectid, null, "output");
}
function shareProject(projectid) {
    divid = newDiv("prjdialogue_"+projectid);
    OIajaxCall("/project/share/"+projectid+"/"+divid, null, divid);
    show("prjdialogue_"+projectid);
}
function confirmShareProject(projectid, divid) {
    OIajaxCall("/project/confirmshare/"+projectid, "username="+getValue("usershare_"+divid), "output");
    hide("prjdialogue_"+projectid);
}
function cancelProject(projectid, started) {
    question = "Etes vous sûr de vouloir annuler ce projet ?";
    if(started) question += " La commission reste à votre charge, les autres sommes seront remboursées si les clients acceptent l'annulation.";
    if(confirm(question))
        OIajaxCall("/project/cancel/"+projectid, null, "output");
}
function answerCancelProject(projectid, answer, divid) {
    OIajaxCall("/project/answercancelproject/"+projectid, "answer="+answer, "output");
    clearDiv(divid);
}
function cancelBid(projectid, started) {
    question = "Etes vous sûr de vouloir annuler votre participation ?";
    if(started) question += " Vous serez remboursé si le responsable accepte votre annulation.";
    if(confirm(question))
        OIajaxCall("/project/cancelbid/"+projectid, null, "output");
}
function answerCancelBid(projectid, bidid, answer, divid) {
    OIajaxCall("/project/answercancelbid/"+projectid, "answer="+answer+"&bid="+bidid, "output");
    clearDiv(divid);
}
function deleteProject(projectid) {
    if(confirm("Etes vous sûr de vouloir supprimer définitivement ce projet ?")) {
        OIajaxCall("/project/delete/"+projectid, null, "output");
        clearDiv("spec_"+projectid+"_"+specid);
    }
}
function updateProgress(projectid, progress) {
    progress = Math.round(progress*100);
    OIajaxCall("/project/editprogress/"+projectid, "progress="+progress, "output");
    document.getElementById("progressbar_"+projectid).style.width = progress+"%";
    document.getElementById("progresslabel_"+projectid).innerHTML = progress+"%";
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
