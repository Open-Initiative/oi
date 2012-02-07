oiTable = null;
function setTaskName(div, id, title, view) {
    var titleDiv = document.createElement('div');
    titleDiv.className = "treetitle";
    div.appendChild(titleDiv);
    titleDiv.innerHTML = '<a href="/project/get/'+id+'/'+view+'">'+title+'</a>';
    titleDiv.title = title;
    var newTaskForm = document.createElement("form");
    newTaskForm.id = "newtask_"+id;
    div.appendChild(newTaskForm);
}
function addTask(tasktitle, projectid, userid) {
    var params = "title="+tasktitle+"&inline=1&progress=0";
    if(userid) params += "&assignee="+userid;
    if(projectid) params += "&parent="+projectid;
    answer = OIajaxCall("/project/save/0", params)
    if(answer) {
        task = eval(answer)[0];
        if(window.oiTree) {
            position = oiTree.nodes[projectid].children.length;
            setTaskName(oiTree.addChild(projectid, task.pk, 0, position), task.pk, task.fields.title, viewname);
        }
    }
    return task.pk;
}
function showChildren(projectid) {
    var i, afterid = projectid, children = oiTree.nodes[projectid].children;
    for(var child=children[i=0]; i<children.length; child=children[++i]) {
        oiTable.showLine(child.id, afterid);
        if(oiTree.nodes[child.id].open && oiTree.nodes[child.id].children.length) afterid = showChildren(child.id);
        else afterid = child.id;
    }
    return afterid;
}
function hideChildren(projectid) {
    var i, children = oiTree.nodes[projectid].children;
    for(var child=children[i=0]; i<children.length; child=children[++i]) {
        oiTable.hideLine(child.id, oiTree.selected==child.id);
        if(oiTree.nodes[child.id].open) if(oiTree.nodes[child.id].children.length) hideChildren(child.id);
    }
}
function onExpandNode(projectid) {
    if(oiTree.nodes[projectid].children.length) {
        if(oiTable) showChildren(projectid);
    } else {
        tasks = eval(OIajaxCall("/project/listtasks/"+projectid));
        var i, afterid = projectid;
        for(var task=tasks[i=0]; i<tasks.length; task=tasks[++i]) {
            setTaskName(oiTree.addChild(projectid, task.pk, task.fields.state, i), task.pk, task.fields.title, viewname);
            if(oiTable) oiTable.addFromTask(task, afterid, i%2);
            afterid = task.pk;
        }
    }
    if(window.oiTable) {
        if(oiTree.selected) oiTable.addSpace(oiTree.selected);
        if(oiTable) oiTable.redraw();
    }
}
function onShrinkNode(projectid) {
    if(oiTable) {
        hideChildren(projectid);
        oiTable.redraw();
    }
}
function setActiveTask(projectid, canAdd) {
    if(canAdd) {
        form = document.getElementById("newtask_"+projectid);
        form.onsubmit = function(){addTask(getValue("newtask_title_"+projectid, true),projectid);return false};
        form.innerHTML = '<input type="image" src="/img/icons/addtask.png" alt="'+gettext("New task")+'" title="'+gettext("New task")+'" />'+
            '<input type="text" id="newtask_title_'+projectid+'" class="newtask_title" value="'+gettext("New task")+'" '+
            'onclick="if(this.value==\''+gettext("New task")+'\')this.value=\'\'" onblur="if(!this.value)this.value=\''+gettext("New task")+'\'"/>';
        oiTree.selected = projectid;
        if(oiTable) oiTable.addSpace(projectid);
    }
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
    for(var i=1;i<=5;i++)
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
function toggleHideProject(projectid) {
    OIajaxCall("/project/togglehide/"+projectid, null, "output");
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
    progress = Math.min(Math.round(progress*100), 100);
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
function changeSpecType(divid) {
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    type = getValue("type_"+divid);
    projectid = getValue("projectid_"+divid);
    specid = getValue("specid_"+divid);
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

function OISpot(specDiv, projectid, specid, spotid, x, y, type, title, linkid) {
    this.projectid = projectid;
    this.specid = specid;
    this.spotid = spotid;
    this.x = x;
    this.y = y;
    this.type = type;
    this.title = title;
    this.linkid = linkid;
    
    this.div = document.getElementById(newDiv(specDiv.id));
    this.div.className = 'popup';
    this.div.style.position= "absolute";
    this.div.style.left = this.x+"px";
    this.div.style.top = this.y+"px";
    this.div.style.display = 'none';
    this.div.spot = this;
    this.fillDiv();
    this.div.onclick = function(evt) {evt.stopPropagation();return false;};
    
    this.img = document.createElement("img");
    this.img.src = "/img/spot1.png";
    this.img.style.position= "absolute";
    this.img.style.left = this.x+"px";
    this.img.style.top = this.y+"px";
    this.img.spot = this;
    this.img.onclick = function(evt) {this.spot.show();evt.stopPropagation();return false;};
    specDiv.appendChild(this.img);
}
OISpot.prototype.edit = function edit() {
    OIajaxCall('/project/'+this.projectid+'/editspot/'+this.specid+"/"+this.x+"/"+this.y, null, this.div.id);
    this.show();
}
OISpot.prototype.fillDiv = function fillDiv() {
    this.div.innerHTML = "";
    if(!this.type) return;
    var content = "";
    if(this.type == 2) content += "<a href='/project/get/"+this.linkid+"'>";
    if(this.type == 3) content += "<a href='#message_"+this.linkid+"_box'>";
    content += this.title;
    if(this.type==2 || this.type==3) content += "</a>";
    content += " <img src='/img/icons/edit.png' class='clickable' onclick='this.parentElement.spot.edit()'/>";
    content += " <img src='/img/icons/delete.png' class='clickable' onclick='this.parentElement.spot.delete()'/>";
    this.div.innerHTML = content;
}
OISpot.prototype.save = function save() {
    var form = this.div.firstElementChild;
    this.type = form.spottype.value;
    if(this.type == 1) this.title = form.note.value;
    if(this.type == 2) {
        this.title = form.tasktitle.value;
        form.taskid.value = addTask(this.title, this.projectid);
        this.linkid = form.taskid.value;
    }
    if(this.type == 3) {
        var divid = newDiv("discussions_"+this.projectid);
        var params = "message="+form.messagebody.value.replace(/\+/gi,"%2B")+
        "&title="+form.messagetitle.value.replace(/\+/gi,"%2B")+"&project="+this.projectid;
        OIajaxCall("/message/save/0", params, divid);
        form.messageid.value = document.getElementById(divid).firstElementChild.id.split('_')[1];
        this.title = form.messagetitle.value;
        this.linkid = form.messageid.value;
    }
    OIajaxCall('/project/'+this.projectid+'/savespot/'+this.specid+'/0', prepareForm('spotform'), 'output');
    this.fillDiv();
    return false;
}
OISpot.prototype.show = function show() {
    this.div.style.display = "block";
    addPopup(this.div);
}
OISpot.prototype.delete = function delete() {
    if(confirm(gettext("Are you sure you want to permanently delete this annotation?"))) {
        OIajaxCall('/project/'+this.projectid+'/deletespot/'+this.specid+'/'+this.spotid, null, 'output');
        this.img.parentElement.removeChild(this.img);
        this.div.parentElement.removeChild(this.div);
    }
}

function deltmp(projectid,filename,ts,divid) {
    OIajaxCall("/project/"+projectid+"/deltmp", "filename="+filename+"&ts="+ts+"&divid="+divid, "output");
    changeFile(divid);
}

function changeFile(divid) {
    document.getElementById("filediv_"+divid).style.display="inline";
    document.getElementById("filespan_"+divid).style.display="none";
}
