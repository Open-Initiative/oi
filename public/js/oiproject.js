oiTable = null;
function setTaskName(div, id, title, view) {
    var titleDiv = document.createElement('div');
    titleDiv.className = "treetitle";
    div.appendChild(titleDiv);
    titleDiv.innerHTML = '<a href="/project/'+id+'/view/'+view+'">'+title+'</a>';
    titleDiv.title = title;
    var newTaskForm = document.createElement("form");
    newTaskForm.id = "newtask_"+id;
    div.parentNode.insertBefore(newTaskForm,div.nextSibling);
}
function addTask(tasktitle, projectid, userid, callBack) {
    var params = "title="+tasktitle+"&inline=1&progress=0";
    if(userid) params += "&assignee="+userid;
    if(projectid) params += "&parent="+projectid;
    OIajaxCall("/project/save/0", params, null, 
        function(response){
            task = eval(response)[0];
            if(window.oiTree) {
                setTaskName(oiTree.nodes[projectid].addChild(task.pk, 0), task.pk, task.fields.title, viewname);
                if(oiTable) {
                    oiTable.addFromTask(task, oiTree.nodes[projectid].getLastChild());
                    oiTable.redraw();
                }
            }
            if(callBack) callBack(task.pk);
        }); 
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
    }else{
	    OIajaxCall("/project/listtasks/"+projectid, null, null, function(response){
            var tasks = eval(response);
            var i, afterid = projectid;
            for(var task=tasks[i=0]; i<tasks.length; task=tasks[++i]) {
                setTaskName(oiTree.nodes[projectid].addChild(task.pk, task.fields.state), task.pk, task.fields.title, viewname);
                if(oiTable) oiTable.addFromTask(task, afterid, i%2);
               	afterid = task.pk;
       	    }
    	});
	}
    if(window.oiTable){
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
function onMoveNode(taskid, newParentid, afterid) {
    var params = "parent="+newParentid;
    if(afterid) params += "&after="+afterid;
    if(OIajaxCall("/project/move/"+taskid, params, "output")) {
        if(oiTable) {
            oiTable.hideLine(taskid);
            if(afterid) oiTable.showLine(taskid, afterid)
            else if(oiTree.nodes[newParentid].open) oiTable.showLine(taskid, oiTree.nodes[newParentid].getLastChild());
            oiTable.redraw();
        }
        return true;
    } else return false;
}
function setActiveTask(projectid, canAdd) {
    oiTree.nodes[projectid].titleDiv.children[0].id = "selected";
    if(canAdd) {
        var form = document.getElementById("newtask_"+projectid);
        form.onsubmit = function(){addTask(getValue("newtask_title_"+projectid, true),projectid);return false};
        form.style.margin = "5px 0";
        form.style.width = "220px";
        form.innerHTML = '<input type="image" src="/img/icons/addtask.png" alt="'+gettext("New task")+'" title="'+gettext("New task")+'" />'+
            '<input type="text" id="newtask_title_'+projectid+'" class="newtask_title" value="'+gettext("New task")+'" '+
            'onclick="if(this.value==\''+gettext("New task")+'\')this.value=\'\'" onblur="if(!this.value)this.value=\''+gettext("New task")+'\'"/>';
        oiTree.selected = projectid;
        if(oiTable) oiTable.addSpace(projectid);
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
    OIajaxCall("/project/confirmedittitle/"+projectid, "title="+title, "output", 
        function(){resetProjectTitle(projectid, title);});
}
function resetProjectTitle(projectid, title) {
    document.getElementById("prjtitle_"+projectid).innerHTML = title;
    document.getElementById("prjtitle_"+projectid).innerHTML += ' <img onclick="editProjectTitle('+projectid+')" class="clickable" src="/img/icons/edit.png" />';
}
function bidProject(projectid, rating) {
    OIajaxCall("/project/bid/"+projectid, null, "prjdialogue_"+projectid,
        function(){show("prjdialogue_"+projectid);
        document.getElementById('bid_'+projectid).focus();});
}
function confirmBidProject(projectid) {
    if(document.getElementById("acceptcgu").checked){
        OIajaxCall("/project/confirmbid/"+projectid, "bid="+getValue("bid_"+projectid), "output", 
            function(){hide("prjdialogue_"+projectid);});
    } else {
        alert(gettext("Please accept the Terms of Use"));
    }
}
function offerProject(projectid) {
    OIajaxCall("/project/offer/"+projectid, null, "prjdialogue_"+projectid, 
        function(){show("prjdialogue_"+projectid);
        document.getElementById('offer_'+projectid).focus();});
}
function confirmOfferProject(projectid) {
    if(document.getElementById("acceptcgu").checked){
        OIajaxCall("/project/confirmoffer/"+projectid, "offer="+getValue("offer_"+projectid), "output", 
        function(){hide("prjdialogue_"+projectid);});  
    } else {
        alert(gettext("Please accept the Terms of Use"));
    }
}
function delegateProject(projectid) {
    OIajaxCall("/project/delegate/"+projectid, null, "prjdialogue_"+projectid, 
        function(){show("prjdialogue_"+projectid);});
}
function confirmDelegateProject(projectid) {
    OIajaxCall("/project/confirmdelegate/"+projectid, "delegate_to="+getValue("delegate_to_"+projectid), "output",
        function(){hide("prjdialogue_"+projectid);});
}
function startProject(projectid) {
    if(confirm(gettext("Are you sure you want to start this task?")))
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
    OIajaxCall("/project/eval/"+projectid, null, "prjdialogue_"+projectid, 
        function(){show("prjdialogue_"+projectid);});
}
function confirmEvalProject(projectid) {
    OIajaxCall("/project/confirmeval/"+projectid, "rating="+getValue(projectid+"_eval")+"&comment="+getValue("eval_comment_"+projectid), "output", 
        function(){hide("prjdialogue_"+projectid);});
}
function toggleHideProject(projectid) {
    OIajaxCall("/project/togglehide/"+projectid, null, "output");
}
function shareProject(projectid) {
    OIajaxCall("/project/share/"+projectid+"/"+divid, null, "prjdialogue_"+projectid, 
        function(){show("prjdialogue_"+projectid);});
}
function confirmShareProject(projectid, divid) {
    OIajaxCall("/project/confirmshare/"+projectid, "username="+getValue("usershare_"+divid), "output", 
        function(){hide("prjdialogue_"+projectid);});
}
function cancelProject(projectid, state) {
    question = gettext("Are you sure you want to cancel this task?");
    if(state > 1) question += gettext(" You will still pay the commission, other amounts will be reimbursed if clients accept cancellation.");
    if(confirm(question))
        OIajaxCall("/project/cancel/"+projectid, null, "output");
}
function answerDelegate(projectid, answer, divid) {
    OIajaxCall("/project/answerdelegate/"+projectid, "answer="+answer, "output", 
        function(){clearDiv(divid);});
}
function answerCancelProject(projectid, answer, divid) {
    OIajaxCall("/project/answercancelproject/"+projectid, "answer="+answer, "output",
        function(){clearDiv(divid);});
}
function answerDelayProject(projectid, answer, divid) {
    OIajaxCall("/project/answerdelay/"+projectid, "answer="+answer, "output", 
        function(){clearDiv(divid);});
}
function cancelBid(projectid, started) {
    question = gettext("Are you sure you want to cancel your bid?");
    if(started) question += gettext(" You will be reimbursed if the project assignee accepts the cancellation. The commission stays at your expense.");
    if(confirm(question))
        OIajaxCall("/project/cancelbid/"+projectid, null, "output");
}
function answerCancelBid(projectid, bidid, answer, divid) {
    OIajaxCall("/project/answercancelbid/"+projectid, "answer="+answer+"&bid="+bidid, "output", 
        function(){clearDiv(divid);});
}
function deleteProject(projectid) {
    if(confirm(gettext("Are you sure you want to delete this task permanently?"))) {
        OIajaxCall("/project/delete/"+projectid, null, "output");
    }
}
function updateProgress(projectid, progress) {
    progress = Math.min(Math.round(progress*100), 100);
    OIajaxCall("/project/editprogress/"+projectid, "progress="+progress, "output", 
        function(){document.getElementById("progressbar_"+projectid).style.width = progress+"%";
        document.getElementById("progresslabel_"+projectid).innerHTML = progress+"%";});
}
function favProject(projectid, param){
    OIajaxCall("/project/"+projectid+"/fav", param, null, 
        function(follow){
            if(document.getElementById("fav_"+projectid)){
            document.getElementById("fav_"+projectid).src = "/img/icons/star"+follow+".png";
            }
        });
}

function addSpec(projectid, specorder) {
    var divid;
    if(!specorder) specorder = -1;
    if(specorder==-1) divid = newDiv("specs_"+projectid);
    else divid = newDivTop("spec_"+projectid+"_"+specorder);
    OIajaxCall("/project/"+projectid+"/editspec/0?divid="+divid+"&specorder="+specorder, null, divid, 
        function(){changeSpecType(divid, 1);});
        document.getElementById(divid).scrollIntoView();
}
function editSpec(projectid, specorder) {
    specid = getValue("specid_"+specorder);
    divid = "spec_"+projectid+"_"+specorder;
    OIajaxCall("/project/"+projectid+"/editspec/"+specid+"?divid="+divid, null, divid,
        function(){changeSpecType(divid, getValue("type_"+divid));});
}
function changeSpecType(divid, type) {
    if(getValue("type_"+divid)==1)tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    projectid = getValue("projectid_"+divid);
    specid = getValue("specid_"+divid);
    document.getElementById("type"+getValue("type_"+divid)+"_"+divid).className = "spectype";
    document.getElementById("type"+type+"_"+divid).className = "spectype spectypeselected";
    document.getElementById("type_"+divid).value = type;
    url = "/project/"+projectid+"/editspecdetails/"+specid+"?divid="+divid+"&type="+type;
    OIajaxCall(url, null, "spec_"+divid, 
        function(){if(getValue("type_"+divid)==1)tinyMCE.execCommand('mceAddControl', false, 'text_'+divid);});
}
function saveSpec(divid, projectid, order, specid) {
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    var params = "text="+getValue("text_"+divid).replace(/\+/gi,"%2B") + "&order="+order + "&type="+getValue("type_"+divid);
    if(getValue("url_"+divid)) params+="&url="+getValue("url_"+divid);
    if(getValue("filename_"+divid)) params+="&filename="+getValue("filename_"+divid);
    if(getValue("ts_"+divid)) params+="&ts="+getValue("ts_"+divid);
    if(getValue("image_"+divid)) params+="&image="+getValue("image_"+divid);
    OIajaxCall("/project/"+projectid+"/savespec/"+specid, params, divid);
}
function deleteSpec(projectid, specorder) {
    if(confirm(gettext("Are you sure you want to delete this specification permanently?"))) {
        specid = getValue("specid_"+specorder);
        OIajaxCall("/project/"+projectid+"/deletespec/"+specid, null, "output", 
            function(){clearDiv("spec_"+projectid+"_"+specorder);});
    }
}

function OISpot(specDiv, projectid, specid, spotid, x, y, title, linkid, number) {
    this.projectid = projectid;
    this.specid = specid;
    this.spotid = spotid;
    this.x = x;
    this.y = y;
    this.title = title;
    this.linkid = linkid;

    this.div = document.getElementById(newDiv(specDiv.id));
    this.div.className = 'popup';
    this.positionelt(this.div, 20);
    this.div.style.display = 'none';
    this.div.spot = this;
    this.fillDiv();
    this.div.onclick = function(evt) {document.ignoreClosePopups = true;evt.stopPropagation();};
    
    this.number = document.createElement("span");
    this.number.innerHTML = number||"";
    this.positionelt(this.number);
    this.number.className = "spotnumber";
    this.number.spot = this;
    this.number.onmouseover = function(evt) {if(!window.draggedDiv)this.spot.show();return false;};
    this.number.onmousedown = this.drag;
    specDiv.appendChild(this.number);
}
OISpot.prototype.drag = function drag(evt) {
    this.spot.hide();
    document.body.style.cursor = "pointer";
    window.draggedDiv = this.spot.number;
    document.onmouseup = window.draggedDiv.spot.drop;
    document.body.appendChild(window.draggedDiv);
    window.draggedDiv.style.top=(evt.clientY+window.pageYOffset-10)+"px";
    window.draggedDiv.style.left=(evt.clientX+window.pageXOffset-10)+"px";
    document.onmousemove= function(evt){
        window.draggedDiv.style.top=(evt.clientY+window.pageYOffset-10)+"px";
        window.draggedDiv.style.left=(evt.clientX+window.pageXOffset-10)+"px";
    }
    return false;
}
OISpot.prototype.drop = function drop(evt) {
    window.draggedDiv.spot.div.parentElement.appendChild(window.draggedDiv);
    var target = evt.target;
    while(target && !target.receiveSpot) target = target.parentNode;
    if(target) target.receiveSpot(window.draggedDiv.spot, evt);
    window.draggedDiv = null;
    document.onmouseup = null;
    document.onmousemove = null;
    document.body.style.cursor = "default";
    return false;
}
OISpot.prototype.positionelt = function positionelt(elt, delta) {
    elt.style.position= "absolute";
    elt.style.left = this.x+(delta||0)+"px";
    elt.style.top = this.y+(delta||0)+"px";
}
OISpot.prototype.edit = function edit() {
    var formdiv = document.getElementById("newspot").cloneNode(true);
    formdiv.style.display = "block";
    this.div.appendChild(formdiv);
    this.show();
}
OISpot.prototype.fillDiv = function fillDiv() {
    if(this.linkid) OIajaxCall('/project/'+this.linkid+'/summarize', null, this.div.id);
}
OISpot.prototype.saveTask = function saveTask() {
    addTask(jQuery('#'+this.div.id+' .newtask_title')[0].value, this.projectid, null, 
        makeObjectCallback(this.save, this));
    return false;
}
OISpot.prototype.save = function save(taskid) {
    this.linkid = taskid;
    OIajaxCall('/project/'+this.projectid+'/savespot/'+this.specid+'/0', "taskid="+this.linkid+ "&x="+this.x + "&y="+this.y, null, makeObjectCallback(function(response){
            var spot = eval(response)[0];
            this.spotid = spot.pk;
            this.number.innerHTML = spot.fields.number;
            this.fillDiv();
        }, this));
    return false;
}
OISpot.prototype.show = function show() {
    this.div.style.display = "block";
    addPopup(this);
}
OISpot.prototype.hide = function hide() {
    this.div.style.display = "none";
    if(!this.linkid) {
        this.number.style.display = "none";
    }
}
OISpot.prototype.move = function move(x,y) {
    this.x = x;
    this.y = y;
    this.positionelt(this.div, 20);
    this.positionelt(this.number);
    OIajaxCall('/project/'+this.projectid+'/savespot/'+this.specid+'/'+this.spotid, "taskid="+this.linkid+ "&x="+this.x + "&y="+this.y)
}
OISpot.prototype.remove = function remove() {
    if(confirm(gettext("Are you sure you want to permanently remove this annotation?"))) {
        OIajaxCall('/project/'+this.projectid+'/removespot/'+this.specid+'/'+this.spotid, null, 'output',
            makeObjectCallback(function(){
            this.div.parentElement.removeChild(this.div);
            this.number.parentElement.removeChild(this.number);}, this));
    }
}
function getSpot(element) {
    while(element) {
        if(element.spot) return element.spot;
        element = element.parentNode;
    }
    return null;
}
function deltmp(projectid,filename,ts,divid) {
    OIajaxCall("/project/"+projectid+"/deltmp", "filename="+filename+"&ts="+ts+"&divid="+divid, "output", 
        function(){changeFile(divid);});
}

function changeFile(divid) {
    document.getElementById("filediv_"+divid).style.display="inline";
    document.getElementById("filespan_"+divid).style.display="none";
}
