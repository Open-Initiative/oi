function addTask(tasktitle, projectid, userid) {
    url = "/project/save/0";
    params = "title="+tasktitle+"&assignee="+userid+"&progress=0&inline=1&parent="+projectid;
    divid = newDiv("tasks_"+projectid);
//    document.getElementById("tasks_"+projectid).className = "pile";
    OIajaxCall(url, params, divid);
    return false;
}
function listTasks(projectid){
    document.getElementById("treebtn_"+projectid).src = "/img/icons/treebtn1-open.png";
    document.getElementById("treebtn_"+projectid).onclick = function(){shrinkTask(projectid);};
    div = document.getElementById("tasks_"+projectid);
    tasks = eval(OIajaxCall("/project/listtasks/"+projectid));
    for(task=tasks[i=0];i<tasks.length;task=tasks[++i]) {
        var state = task.fields.state?task.fields.state:1;
        div = document.getElementById(newDiv("tasks_"+projectid));
        div.className = "task"+state;
        div.innerHTML = '<img id="treebtn_'+task.pk+'" src="/img/icons/treebtn'+state+'-closed.png" onclick="listTasks('+task.pk+')"/>'+
            '<a href="/project/get/'+task.pk+'">'+task.fields.title+'</a>'+
            '<form id="newtask_'+task.pk+'"></form>'+'<div class="tasklist" id="tasks_'+task.pk+'"></div>';
        if(typeof(gantt)!="undefined")
            gantt.addBar(task.pk, [parseDate(task.fields.created),parseDate(task.fields.start_date),parseDate(task.fields.due_date)], projectid);
    }
}
function shrinkTask(projectid) {
    document.getElementById("tasks_"+projectid).innerHTML = "";
    document.getElementById("treebtn_"+projectid).src = "/img/icons/treebtn1-closed.png";
    document.getElementById("treebtn_"+projectid).onclick = function(){listTasks(projectid);};
}
function setActiveTask(projectid) {
    form = document.getElementById("newtask_"+projectid);
    form.onsubmit = function(){return addTask(getValue("newtask_title_"+projectid, true),projectid,username);};
    form.innerHTML = '<input type="image" src="/img/icons/addtask.png" alt="'+gettext("New task")+'" title="'+gettext("New task")+'" />'+
        '<input type="text" id="newtask_title_'+projectid+'" class="newtask_title" value="'+gettext("New task")+'"/>';
    if(typeof(gantt)!="undefined")
        gantt.addSpace(projectid);
}
function copyTask(taskid, tasktitle) {
    OIajaxCall("/project/copy/"+taskid, null, "output");
    div = document.getElementById("project_clipboard");
    div.innerHTML += '<div id="project_clipboard_'+taskid+'">' +
        '<img class="clickable" src="/img/icons/delete.png" title="'+gettext('remove from clipboard')+'" onclick="uncopyTask('+taskid+')"/> ' +
        tasktitle + '</div>';
}
function uncopyTask(taskid) {
    OIajaxCall("/project/uncopy/"+taskid, null, "output");
    clearDiv("project_clipboard_"+taskid);
}
function pasteTasks(projectid) {
    if(confirm(gettext("Do you want to empty the clipboard and move all tasks it contains to this project?"))) {
        OIajaxCall("/project/paste/"+projectid, null, "output");
    }
}
function editDate(projectid, field_name, date) {
    OIajaxCall("/project/editdate/"+projectid, "field_name="+field_name+"&date="+date.dateFormat("Y-m-d"), "output");
}
function editProjectTitle(projectid) {
    OIajaxCall("/project/edittitle/"+projectid, null, "prjtitle_"+projectid);
}
function confirmEditTitle(projectid) {
    title = getValue("title_"+projectid);
    OIajaxCall("/project/confirmedittitle/"+projectid, "title="+title, "output");
    resetProjectTitle(projectid, title);
}
function resetProjectTitle(projectid, title) {
    document.getElementById("prjtitle_"+projectid).innerHTML = title;
    document.getElementById("prjtitle_"+projectid).innerHTML += ' <img onclick="editProjectTitle('+projectid+')" class="clickable" src="/img/icons/edit.png" />';
}
function bidProject(projectid, rating) {
    OIajaxCall("/project/bid/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
    document.getElementById('bid_'+projectid).focus();
}
function confirmBidProject(projectid) {
    if(document.getElementById("acceptcgu").checked){
        OIajaxCall("/project/confirmbid/"+projectid, "bid="+getValue("bid_"+projectid), "output");
        hide("prjdialogue_"+projectid);
    } else {
        alert(gettext("Please accept the Terms of Use"));
    }
}
function offerProject(projectid) {
    OIajaxCall("/project/offer/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
    document.getElementById('offer_'+projectid).focus();
}
function confirmOfferProject(projectid) {
    if(document.getElementById("acceptcgu").checked){
        OIajaxCall("/project/confirmoffer/"+projectid, "offer="+getValue("offer_"+projectid), "output");
        hide("prjdialogue_"+projectid);
    } else {
        alert(gettext("Please accept the Terms of Use"));
    }
}
function delegateProject(projectid) {
    OIajaxCall("/project/delegate/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
}
function confirmDelegateProject(projectid) {
    OIajaxCall("/project/confirmdelegate/"+projectid, "delegate_to="+getValue("delegate_to_"+projectid), "output");
    hide("prjdialogue_"+projectid);
}
function startProject(projectid) {
    if(confirm(gettext("Are you sure you want to start this project?")))
        OIajaxCall("/project/start/"+projectid, null, "output");
}
function deliverProject(projectid) {
    OIajaxCall("/project/deliver/"+projectid, null, "output");
}
function validateProject(projectid) {
    OIajaxCall("/project/validate/"+projectid, null, "output");
}
function showStar(id, number) {
    for(i=1;i<=5;i++)
        if(i<=number) document.getElementById("star"+i+"_"+id).src = document.getElementById("star"+i+"_"+id).src.replace("False","True");
        else document.getElementById("star"+i+"_"+id).src = document.getElementById("star"+i+"_"+id).src.replace("True","False");
}
function setStar(id, dest, number) {
    showStar(id, number);
    document.getElementById(dest).value = number;
}
function resetStar(id, dest) {
    number = parseInt(getValue(dest));
    showStar(id, number);
}
function setPriority(projectid) {
    OIajaxCall("/project/setpriority/"+projectid, "priority="+getValue(projectid+"_priority"), "output");
}
function evalProject(projectid, rating) {
    OIajaxCall("/project/eval/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
}
function confirmEvalProject(projectid) {
    OIajaxCall("/project/confirmeval/"+projectid, "rating="+getValue(projectid+"_eval")+"&comment="+getValue("eval_comment_"+projectid), "output");
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
    question = gettext("Are you sure you want to cancel this project?");
    if(started) question += gettext(" You will still pay the commission, other amounts will be reimbursed if clients accept cancellation.");
    if(confirm(question))
        OIajaxCall("/project/cancel/"+projectid, null, "output");
}
function answerDelegate(projectid, answer, divid) {
    OIajaxCall("/project/answerdelegate/"+projectid, "answer="+answer, "output");
    clearDiv(divid);
}
function answerCancelProject(projectid, answer, divid) {
    OIajaxCall("/project/answercancelproject/"+projectid, "answer="+answer, "output");
    clearDiv(divid);
}
function answerDelayProject(projectid, answer, divid) {
    OIajaxCall("/project/answerdelay/"+projectid, "answer="+answer, "output");
    clearDiv(divid);
}
function cancelBid(projectid, started) {
    question = gettext("Are you sure you want to cancel your bid?");
    if(started) question += gettext(" You will be reimbursed if the project assignee accepts the cancellation. The commission stays at your expense.");
    if(confirm(question))
        OIajaxCall("/project/cancelbid/"+projectid, null, "output");
}
function answerCancelBid(projectid, bidid, answer, divid) {
    OIajaxCall("/project/answercancelbid/"+projectid, "answer="+answer+"&bid="+bidid, "output");
    clearDiv(divid);
}
function deleteProject(projectid, messageid) {
    if(confirm(gettext("Are you sure you want to delete this project permanently?"))) {
        OIajaxCall("/project/delete/"+projectid, null, "output");
    }
}
function moveProject(projectid) {
    OIajaxCall("/project/move/"+projectid, null, "prjdialogue_"+projectid);
    show("prjdialogue_"+projectid);
}
function confirmMoveProject(projectid) {
    OIajaxCall("/project/confirmmove/"+projectid, "parent="+getValue("parent_"+projectid), "output");
    hide("prjdialogue_"+projectid);
}
function updateProgress(projectid, progress) {
    progress = Math.round(progress*100);
    OIajaxCall("/project/editprogress/"+projectid, "progress="+progress, "output");
    document.getElementById("progressbar_"+projectid).style.width = progress+"%";
    document.getElementById("progresslabel_"+projectid).innerHTML = progress+"%";
}
function observeProject(prjid, param){
    OIajaxCall("/project/observe/"+prjid, param, "output");
}
function addSpec(projectid, specorder) {
    if(specorder==-1) divid = newDiv("specs_"+projectid);
    else divid = newDivTop("spec_"+projectid+"_"+specorder);
    OIajaxCall("/project/"+projectid+"/editspec/0?divid="+divid+"&specorder="+specorder, null, divid);
    document.getElementById(divid).scrollIntoView();
    changeSpecType(divid);
}
function editSpec(projectid, specorder) {
    specid = getValue("specid_"+specorder);
    divid = "spec_"+projectid+"_"+specorder;
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
function deleteSpec(projectid, specorder) {
    if(confirm(gettext("Are you sure you want to delete this specification permanently?"))) {
        specid = getValue("specid_"+specorder);
        OIajaxCall("/project/"+projectid+"/deletespec/"+specid, null, "output");
        clearDiv("spec_"+projectid+"_"+specorder);
    }
}
function deltmp(projectid,filename,ts,divid) {
    if(confirm(gettext("Are you sure you want to delete this attachment permanently?"))) {
        OIajaxCall("/project/"+projectid+"/deltmp", "filename="+filename+"&ts="+ts+"&divid="+divid, "output");
        changeFile(divid);
    }
}

function changeFile(divid) {
    document.getElementById("filediv_"+divid).style.display="inline";
    document.getElementById("filespan_"+divid).style.display="none";
}
