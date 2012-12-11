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
function addTask(tasktitle, projectid, callBack) {
    var params = "title="+tasktitle+"&inline=1&progress=0";
    if(projectid) params += "&parent="+projectid;
    OIajaxCall("/project/save/0", params, null, 
        function(response){
            var task = eval(response)[0];
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
function populateTaskList(taskLists) {
    var j;
    for(var list=taskLists[j=0]; j<taskLists.length; list=taskLists[++j]) {
        var i, afterid=0;
        var tasks = eval(list);
        for(var task=tasks[i=0]; i<tasks.length; task=tasks[++i]) {
            var parentid = task.fields.parent;
            setTaskName(oiTree.nodes[String(parentid).replace(".","")].addChild(task.pk, task.fields.state), task.pk, task.fields.title, viewname);
            if(oiTable) oiTable.addFromTask(task, afterid||parentid, i%2);
            afterid = task.pk;
        }
    }
}
function addRelease(projectid){
    var value = prompt(gettext("Enter your text :"));
    if(value){ 
        OIajaxCall("/project/"+projectid+"/addrelease", "release="+value, "output", 
            function(){
                document.getElementById("release").appendChild(document.createElement("option")).innerHTML = value;
                document.getElementById("nextrelease").appendChild(document.createElement("option")).innerHTML = value;
            }
        );
    }
    return value;
}
function changeRelease(projectid){
    if (document.getElementById("change_release").selected) name = addRelease(projectid);
    else name = getValue("nextrelease");
    if(name){
        if(confirm(
        gettext("Are you sure you want to mark '")+ getValue("release") +gettext("' as done and work on '")+ name +gettext("'. All unfinished tasks in '")+ getValue("release") +gettext("' will be assigned to '")+ name +"'.")){
            OIajaxCall("/project/"+projectid+"/changerelease","release="+name,"output",function(){});
        }
    } 
}
function assignRelease(projectid){
    var value = getValue("entitle-overview_"+projectid);
    if(!value) return
    OIajaxCall("/project/"+projectid+"/assignrelease", "release="+value, "output", 
        function(){
            document.getElementById("assignRelease").innerHTML = ""+value;
        }
    )
}
function onExpandNode(projectid) {
    if(!oiTree.nodes[projectid].children.length){
        OIajaxCall("/project/"+projectid+"/listtasks?release="+getValue("release"), null, null,
            function(response){
                populateTaskList(eval('('+response+')'));
                if(window.oiTable){
                    showChildren(projectid);
                    if(oiTree.selected) oiTable.addSpace(oiTree.selected);
                    oiTable.redraw();
                }
            }
        );
    }else{
        if(window.oiTable){
            showChildren(projectid);
            if(oiTree.selected) oiTable.addSpace(oiTree.selected);
            oiTable.redraw();
        }
    }
}
function onShrinkNode(projectid) {
    if(oiTable) {
        hideChildren(projectid);
        oiTable.redraw();
    }
}
function onMoveNode(taskid, newParentid, afterid){
    var params = "parent="+newParentid;
    if(afterid) params += "&after="+afterid;
    OIajaxCall("/project/move/"+taskid, params, "output", 
        function(taskid, newParentid, afterid){
            return function(){
                oiTree.nodes[newParentid].addChild(taskid, 0, afterid);
                if(oiTable) {
                    oiTable.hideLine(taskid);
                    if(afterid){ 
                        oiTable.showLine(taskid, oiTree.nodes[newParentid].getLastChild());
                    }
                    else if(oiTree.nodes[newParentid].open){ oiTable.showLine(taskid, oiTree.nodes[newParentid].getLastChild());
                        oiTable.redraw();
                    }
                }
        }
    }(taskid, newParentid, afterid));
}
function setActiveTask(projectid, canAdd) {
    oiTree.nodes[projectid].titleDiv.children[0].className += " selected"+coloration;
    if(oiTable) oiTable.selectLine(projectid);
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
    OIajaxCall("/project/confirmedittitle/"+projectid, "title="+getValue("title_"+projectid), "output", 
        function(){resetProjectTitle(projectid, getValue("title_"+projectid));});
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
function validatorProject(projectid, rating){
    OIajaxCall("/project/validator/"+projectid, null, "prjdialogue_"+projectid,
        function(){show("prjdialogue_"+projectid);
        document.getElementById('validator_'+projectid).focus();});
}
function confirmValidatorProject(projectid) {
    OIajaxCall("/project/confirmvalidator/"+projectid, "username="+getValue("validator_"+projectid), "output", 
        function(){hide("prjdialogue_"+projectid);});
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
    if(confirm(gettext("Are you sure you want to deliver this task?")))
        OIajaxCall("/project/deliver/"+projectid, null, "output");
}
function validateProject(projectid) {
    if(confirm(gettext("Are you sure you want to validate this task?")))
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
    showStar(id, parseInt(getValue(dest)));
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
function shareProject(projectid) {
    OIajaxCall("/project/"+projectid+"/share", null, "prjdialogue_"+projectid, 
        function(){show("prjdialogue_"+projectid);
        document.getElementById('usershare_'+projectid).focus();
        });
}
function confirmShareProject(projectid) {
    OIajaxCall("/project/"+projectid+"/confirmshare", "username="+getValue("usershare_"+projectid), "output", 
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
    var progress = Math.min(Math.round(progress*100), 100);
    OIajaxCall("/project/editprogress/"+projectid, "progress="+progress, "output", 
        function(){document.getElementById("progressbar_"+projectid).style.width = progress+"%";
        document.getElementById("progresslabel_"+projectid).innerHTML = progress+"%";});
}
function favProject(projectid){
    OIajaxCall("/project/"+projectid+"/fav", follow?"&stop=true":null, null, 
        function(response){
            if(document.getElementById("fav_"+projectid)){
                document.getElementById("fav_"+projectid).src = "/img/icons/star"+response+".png";
                follow = (response=="True");
            }
        }
    );
}
function orderOverviewTable(projectid, order_by){
    if(order==order_by) order = "-"+order_by;
    else order = order_by;
    populateOverviewTable(projectid);
}
function populateOverviewTable(projectid){
    var divid = "load";
    var url = "/project/"+projectid+"/listtasks?listall";
    if(order) url += "&order="+order;
    url += "&page="+(page||1);
    url += "&"+prepareForm("form_overview");
    document.location.hash = '#'+prepareForm("form_overview");
    OIajaxCall(url, null, divid, 
        function(response){
            var header = document.getElementById('headerTableOverview');
            document.appendChild(header);
            document.getElementById('dynamicTableOverview').innerHTML = "";
            document.getElementById('dynamicTableOverview').appendChild(header);
            var tasklist = eval(eval(response)[0]);
            var fields = ["title", "state", "due_date", "assignee_get_profile_get_display_name", "offer", "target_name"];
            var views = ["overview","description","planning","team","budget","overview"];
            for(var i = 0; i < tasklist.length; i++){
                var line = document.createElement('tr');
                var task = tasklist[i];
                line.className += "state"+task.fields["state"];
                for(var field = fields[j=0]; j < fields.length; field=fields[++j]){
                    if(fields[j]=="state"){
                        if(task.fields[field] == 0){
                            task.fields["due_date"] = ""+task.fields.start_date;
                        }
                        if(task.fields[field] == 1){
                            task.fields["due_date"] = ""+task.fields.due_date;
                        }
                        if(task.fields[field] == 2){
                            task.fields["due_date"] = ""+task.fields.due_date;
                        }
                        if(task.fields[field] == 3){
                            task.fields["due_date"] = ""+task.fields.validation;
                        }
                        if(task.fields[field] == 4){
                            task.fields["due_date"] = ""+task.fields.validation;
                        }
                        task.fields[field] = gettext("State"+task.fields[field]);
                    };
//                    if(fields[j]=="due_date"){if(!task.fields[field]) {task.fields[field]="-";}; };
                    if(fields[j]=="offer")task.fields[field] += " €";
                    if(fields[j]=="target_name"){if(!task.fields[field]) {task.fields[field]="-";}; };
                    line.appendChild(document.createElement('td')).innerHTML = "<a href=/project/"+task.pk+"/view/"+views[j]+">"+task.fields[field]+"</a>";
                }
                document.getElementById('dynamicTableOverview').appendChild(line);
            }if(this.oiTree.nodes[projectid]) this.oiTree.nodes[projectid].className = " invisible";
        document.getElementById('projectOverviewPageNext').style.display = (page >= nbpage?"none":"inline"); 
        document.getElementById('projectOverviewPagePrev').style.display = (page > 1?"inline":"none");
        clearDiv(divid);
        }
    );
}
function addSpec(projectid) {
    var divid = newDiv("specs_"+projectid);
    OIajaxCall("/project/"+projectid+"/editspec/0?divid="+divid+"&specorder=-1", null, divid, 
        function(){changeSpecType(divid, 1);});
        document.getElementById(divid).scrollIntoView();
}
function moveSpec(projectid, specorder, moveUp){
    var div = jQuery("#spec_"+projectid+"_"+specorder);
    var specid = div.find("input").first().val();
    var targetDiv = moveUp?div.prevAll("div").first():div.nextAll("div").first();
    var targetspecid = targetDiv.find("input").first().val();
    if(targetspecid)
        OIajaxCall("/project/"+projectid+"/movespec/"+specid,"target="+targetspecid, "output",
            function (){
                if(moveUp){
                    div.prevAll("div").first().before(div);
                }else{
                    div.nextAll("div").first().after(div);
                }
            });  
}
function editSpec(projectid, specorder) {
    var specid = getValue("specid_"+projectid+"_"+specorder);
    var divid = "spec_"+projectid+"_"+specorder;
    OIajaxCall("/project/"+projectid+"/editspec/"+specid+"?divid="+divid, null, divid,
        function(){changeSpecType(divid, getValue("type_"+divid));});
}
function changeSpecType(divid, type) {
    if(getValue("type_"+divid)==1)tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    var projectid = getValue("projectid_"+divid);
    var specid = getValue("specid_"+divid);
    document.getElementById("type"+getValue("type_"+divid)+"_"+divid).className = "spectype";
    document.getElementById("type"+type+"_"+divid).className = "spectype spectypeselected";
    document.getElementById("type_"+divid).value = type;
    var url = "/project/"+projectid+"/editspecdetails/"+specid+"?divid="+divid+"&type="+type;
    OIajaxCall(url, null, "spec_"+divid, 
        function(){if(getValue("type_"+divid)==1)tinyMCE.execCommand('mceAddControl', false, 'text_'+divid);
            if(getValue("type_"+divid)==6){
                buildText(divid);
                if(document.getElementById("text_"+divid)){
                    document.getElementById("text_"+divid+"_div").style.display = "none";
                }else{
                    document.getElementById("text_"+divid+"_div").style.display = "inline";
                }
            }
        });
}
function prepareText(divid){
    var allvalue = "<dl>";
    allvalue += "<br /><dt><b> What I did: </b></dt><dd>"+document.getElementById("bug_report_"+divid+"_1").value+"</dd>";
    allvalue += "<br /><dt><b> What happened: </b></dt><dd>"+document.getElementById("bug_report_"+divid+"_2").value+"</dd>";
    allvalue += "<br /><dt><b> What should happen: </b></dt><dd>"+document.getElementById("bug_report_"+divid+"_3").value+"</dd>";
    allvalue += "<br /><dt><b> Environnement: </b></dt><dd>"+document.getElementById("bug_report_"+divid+"_4").value+"</dd>";
    
    document.getElementById("text_"+divid).value = allvalue.replace(/\n/g,"<br />")+"</dl>";
}
function buildText(divid){
    if(document.getElementById(divid).getElementsByTagName("dd")){
    for(var i = 1; i <= 4; ++i){
        document.getElementById("bug_report_"+divid+"_"+i).innerHTML = document.getElementById(divid).getElementsByTagName("dd")[i-1].innerHTML.replace(/<br( \/)*>/g, "\n");}
    }
}
function saveSpec(divid, projectid, order, specid) {
    tinyMCE.execCommand('mceRemoveControl', false, 'text_'+divid);
    var params = "text="+getValue("text_"+divid).replace(/\+/gi,"%2B") + "&order="+order + "&type="+getValue("type_"+divid);
    if(getValue("url_"+divid)) params+="&url="+getValue("url_"+divid);
    if(getValue("filename_"+divid)) params+="&filename="+getValue("filename_"+divid);
    if(getValue("ts_"+divid)) params+="&ts="+getValue("ts_"+divid);
    if(getValue("image_"+divid)) params+="&image="+getValue("image_"+divid);
    OIajaxCall("/project/"+projectid+"/savespec/"+specid, params, divid,
        function(divid){
            return function(){
                     var div = document.getElementById(divid);
                     while(div.childNodes.length)
                         div.parentNode.appendChild(div.firstChild);
                     div.parentNode.removeChild(div);
                   }
        }(divid));
}
function deleteSpec(projectid, specorder) {
    if(confirm(gettext("Are you sure you want to delete this specification permanently?"))) {
        var specid = getValue("specid_"+projectid+"_"+specorder);
        OIajaxCall("/project/"+projectid+"/deletespec/"+specid, null, "output", 
            function(){
                var div = document.getElementById("spec_"+projectid+"_"+specorder);
                div.parentNode.removeChild(div);});
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
    this.fillDiv();
    this.div.spot = this;
    this.div.onclick = function(evt) {document.ignoreClosePopups = true;(evt||window.event).stopPropagation();};
    this.div.style.zIndex = 2;
    
    this.number = document.createElement("span");
    this.number.innerHTML = number||"";
    this.positionelt(this.number);
    this.number.className = "spotnumber";
    this.number.style.zIndex = 1;
    this.number.onmouseover = makeObjectCallback(function(evt) {if(!window.draggedSpot)this.show();return false;}, this);
    this.number.onmousedown = makeObjectCallback(this.drag, this);
    specDiv.appendChild(this.number);
}
OISpot.prototype.positionelt = function positioneltSpot(elt, delta) {
    elt.style.position= "absolute";
    elt.style.left = this.x+(delta||0)+"px";
    elt.style.top = this.y+(delta||0)+"px";
}
OISpot.prototype.drag = function dragSpot(evt) {
    var event = evt||window.event;
    window.draggedSpot = this;
    hide(this.div.id);
    document.body.style.cursor = "pointer";
    document.onmouseup = makeObjectCallback(this.drop, this);
    document.body.appendChild(this.number);
    this.number.style.top = (event.clientY+document.documentElement.scrollTop-10)+"px";
    this.number.style.left = (event.clientX+document.documentElement.scrollLeft-10)+"px";
    document.onmousemove= makeObjectCallback(function(evt){
        var event = evt||window.event;
        this.number.style.top = (event.clientY+document.documentElement.scrollTop-10)+"px";
        this.number.style.left = (event.clientX+document.documentElement.scrollLeft-10)+"px";
    }, this);
    return false;
}
OISpot.prototype.drop = function dropSpot(evt) {
    var event = evt||window.event;
    this.div.parentNode.appendChild(this.number);
    this.move(
        (event.pageX||(event.clientX + document.documentElement.scrollLeft))-this.div.parentElement.offsetLeft-10,
        (event.pageY||(event.clientY + document.documentElement.scrollTop))-this.div.parentElement.offsetTop-10);
    document.onmouseup = null;
    document.onmousemove = null;
    document.body.style.cursor = "default";
    window.draggedSpot = null;
    document.ignoreClosePopups = true;
    event.stopPropagation();
    return false;
}
OISpot.prototype.edit = function editSpot() {
    var formdiv = document.getElementById("newspot").cloneNode(true);
    formdiv.style.display = "block";
    this.div.appendChild(formdiv);
    this.show();
}
OISpot.prototype.fillDiv = function fillDiv() {
    if(this.linkid) OIajaxCall('/project/'+this.linkid+'/summarize', null, this.div.id);
}
OISpot.prototype.saveTask = function saveTaskSpot() {
    addTask(jQuery('#'+this.div.id+' .newtask_title')[0].value, this.projectid, makeObjectCallback(this.save, this));
    return false;
}
OISpot.prototype.save = function saveSpot(taskid) {
    this.linkid = taskid;
    OIajaxCall('/project/'+this.projectid+'/savespot/'+this.specid+'/0', "taskid="+this.linkid+ "&x="+this.x + "&y="+this.y, null, makeObjectCallback(function(response){
            var spot = eval(response)[0];
            this.spotid = spot.pk;
            this.number.innerHTML = spot.fields.number;
            this.fillDiv();
        }, this));
    return false;
}
OISpot.prototype.show = function showSpot() {
    this.div.style.display = "block";
    addPopup(this.div);
}
//OISpot.prototype.hide = function hideSpot() {
//    this.div.style.display = "none";
//    if(!(window.draggedSpot || this.linkid))
        //this.number.style.display = "none";
//}
OISpot.prototype.move = function moveSpot(x,y) {
    this.x = x;
    this.y = y;
    this.positionelt(this.div, 20);
    this.positionelt(this.number);
    if(this.spotid)
        OIajaxCall('/project/'+this.projectid+'/savespot/'+this.specid+'/'+this.spotid, "taskid="+this.linkid+ "&x="+this.x + "&y="+this.y);
}
OISpot.prototype.remove = function removeSpot() {
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
