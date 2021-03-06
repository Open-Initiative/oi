oiTable = null;
oiTree = null;
function setTaskName(div, id, title, view) {
    div.innerHTML="";
    var titleDiv = document.createElement('div');
    titleDiv.className = "treetitle";
    div.appendChild(titleDiv);
    titleDiv.innerHTML = '<a href="/prjmgt/'+id+'/view/'+view+'">'+title+'</a>';
    titleDiv.title = title;
    var newTaskForm = document.createElement("form");
    newTaskForm.id = "newtask_"+id;
    div.parentNode.insertBefore(newTaskForm,div.nextSibling);
}
function addTask(tasktitle, projectid, offer, callBack) {
    var params = "title="+tasktitle+"&inline=1&progress=0";
    if(offer) params += "&offer="+offer; 
    if(projectid) params += "&parent="+projectid;
    if(document.getElementById("appname")) params += "&app="+getValue("appname");
    OIajaxCall("/project/save/0", params, null, 
        function(response){
            var task = eval(response)[0];
            if(window.oiTree && oiTree.nodes[projectid]) {
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
            var has_right_to_edit = task.fields.state < 2;
            setTaskName(oiTree.nodes[String(parentid).replace(".","")].addChild(task.pk, task.fields.state, null, task.fields.tasks_count, has_right_to_edit), task.pk, task.fields.title, viewname);
            if(oiTable) oiTable.addFromTask(task, afterid||parentid, i%2);
            afterid = task.pk;
        }
    }
}
function addRelease(projectid){
    var value = prompt(gettext("Please enter the release name:"));
    if(value){ 
        OIajaxCall("/project/"+projectid+"/addrelease", "release="+value, "output", 
            function(){
                var newRelease = ["release","nextrelease","entitle-overview_"+projectid];
                if(document.getElementById(newRelease[i])){
                    for(var i = 0; i < newRelease.length; i++){
                        document.getElementById(newRelease[i]).appendChild(document.createElement("option")).innerHTML = value;
                    }
                }
            }
        );
    }
    return value;
}
function changeRelease(projectid, currentRelease){
    if (document.getElementById("change_release").selected){ 
        name = addRelease(projectid);
        document.getElementById("change_release").selected = false;
    }
    else name = encodeURIComponent(getValue("nextrelease"));
    if(name){
        if(confirm(
        gettext("Are you sure you want to mark '")+ currentRelease +gettext("' as done and work on '")+ name +gettext("'. All unfinished tasks in '")+ currentRelease +gettext("' will be assigned to '")+ name +"'.")){
            OIajaxCall("/project/"+projectid+"/changerelease","release="+name,"output",function(){});
        }
    } 
}
function assignRelease(projectid){
    var value = encodeURIComponent(getValue("entitle-overview_"+projectid));
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
            '<input type="text" id="newtask_title_'+projectid+'" class="newtask_title" placeholder="'+gettext("New task")+'"/>';
        oiTree.selected = projectid;
        if(oiTable) oiTable.addSpace(projectid);
    }
}
function submitProject(){
    $('#projects').fadeToggle(); $('#newproject').fadeToggle();
}
function editDate(projectid, field_name, date) {
    OIajaxCall("/project/editdate/"+projectid, "field_name="+field_name+"&date="+date.dateFormat("Y-m-d"), "output");
}
function confirmEditTitle(projectid, title) {
    OIajaxCall("/project/confirmedittitle/"+projectid, "title="+title, "output", function(){resetProjectTitle(projectid, title);});
}
function resetProjectTitle(projectid, title) {
    if(document.getElementById("prjtitle_"+projectid)){
        document.getElementById("prjtitle_"+projectid).innerHTML = decodeURIComponent(title);
        document.getElementById("prjtitle_"+projectid).innerHTML += '<img onclick="document.getElementById(\'prjtitle_'+projectid+'\').innerHTML = document.getElementById(\'edittitle\').innerHTML" class="clickable" src="/img/icons/edit.png" />';
    }
    if(document.getElementById("feature_"+projectid)) document.getElementById('feature_'+projectid).innerHTML = title;
    if(oiTree) setTaskName(oiTree.nodes[projectid].titleDiv, projectid, title, viewname);
}
function confirmBidProject(projectid) {
    if(document.getElementById("acceptcgubid").checked){
        OIajaxCall("/project/confirmbid/"+projectid, "bid="+getValue("bid_"+projectid), "output", 
            function(){hide("prjdialoguebid_"+projectid);});
    } else {
        alert(gettext("Please accept the Terms of Use"));
    }
}
function confirmValidatorProject(projectid) {
    OIajaxCall("/project/confirmvalidator/"+projectid, "username="+getValue("validator_"+projectid), "output", 
        function(){hide("prjdialoguevalidator_"+projectid);});
}
function confirmOfferProject(projectid) {
    if(document.getElementById("acceptcguoffer").checked){
        OIajaxCall("/project/confirmoffer/"+projectid, "offer="+getValue("offer_"+projectid), "output", 
        function(){hide("prjdialogueoffer_"+projectid);});  
    } else {
        alert(gettext("Please accept the Terms of Use"));
    }
}
function confirmDelegateProject(projectid) {
    OIajaxCall("/project/confirmdelegate/"+projectid, "delegate_to="+getValue("delegate_to_"+projectid), "output",
        function(){hide("prjdialoguedelegate_"+projectid);});
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
function confirmEvalProject(projectid) {
    OIajaxCall("/project/confirmeval/"+projectid, "rating="+getValue(projectid+"_eval")+"&comment="+getValue("eval_comment_"+projectid), "output", 
        function(){hide("prjdialogueeval_"+projectid);});
}
function confirmShareProject(projectid) {
    OIajaxCall("/project/"+projectid+"/confirmshare", "username="+getValue("usershare_"+projectid), "output", 
        function(){hide("prjdialogueshare_"+projectid);});
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
        OIajaxCall("/project/delete/"+projectid, null, "output",
            function(){
                if(currentTask == projectid){
                    if(oiTree.nodes[projectid].parent) document.location = "/prjmgt/"+oiTree.nodes[projectid].parent.id;
                    else document.location = "/";
                } else {
                       if(oiTree) oiTree.deleteNode(projectid);
                }
        });
    }
}
function updateProgress(projectid, progress) {
    var progress = Math.min(Math.round(progress*100), 100);
    OIajaxCall("/project/editprogress/"+projectid, "progress="+progress, "output", 
        function(){document.getElementById("progressbar_"+projectid).style.width = progress+"%";
        document.getElementById("progresslabel_"+projectid).innerHTML = progress+"%";});
}
function favProject(projectid, val){
    OIajaxCall("/project/"+projectid+"/fav", follow?"&stop=true":false, null, 
        function(response){
            if(document.getElementById("fav_"+projectid)){
                // check if the platform is fundig
                if(val){ 
                    var localhost = "Funding";
                    if($("#fav_"+projectid+"_com").html()==gettext("Follow the project")){
                        $("#fav_"+projectid+"_com").html(gettext("Stop following the project"));
                    }else{
                        $("#fav_"+projectid+"_com").html(gettext("Follow the project"));
                    }
                }else{ 
                    var localhost = "";
                }
                document.getElementById("fav_"+projectid).src = "/img/icons/star"+response+localhost+".png";
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
function urlOverview(projectid){
    var params = "";
    var url = "";
    url += "&"+prepareForm("form_overview");   // I don't know why, but I need it for filter on overview table 
    for(var i = 0; i < prepareForm("form_overview").split("&").length; i++){
        if(prepareForm("form_overview").split("&")[i].split("=")[1]){
            params += prepareForm("form_overview").split("&")[i]+"&";
        }
    } 
    document.location.hash = params;
    return url;
}
function paginateOverviewTable(projectid, paginator, nbpage){
    if(this.oiTree.nodes[projectid]) this.oiTree.nodes[projectid].className = " invisible";
    document.getElementById('projectOverviewPageNext').style.display = (page >= nbpage?"none":"inline"); 
    document.getElementById('projectOverviewPagePrev').style.display = (page > 1?"inline":"none");
    clearDiv("load_"+projectid);
    document.getElementById("nbpage").innerHTML = nbpage;
    document.getElementById('page').innerHTML = page;
    document.getElementById("nbfiltrepage").innerHTML = paginator.nbtask+gettext(" out of ");
}
function populateOverviewTable(projectid){
    var url = "/project/"+projectid+"/listtasks?listall";
    if(order) url += "&order="+order;
    url += "&page="+page;
    var param = urlOverview(projectid);
    OIajaxCall(url+param, null, "load_"+projectid, 
        function(response){
            var header = document.getElementById('headerTableOverview');
            document.getElementById('dynamicTableOverview').innerHTML = "";
            document.getElementById('dynamicTableOverview').appendChild(header);
            paginator = eval(response)[0];
            nbpage = paginator.num_pages;
            var tasklist = eval(eval(response)[1]);
            var fields = ["title", "state", "due_date", "assignee_get_profile_get_display_name", "offer", "target_name"];
            var views = ["overview","description","planning","team","budget","overview"];
            for(var i = 0; i < tasklist.length; i++){
                var line = document.createElement('tr');
                var task = tasklist[i];
                line.className += "state"+task.fields["state"];
                for(var field = fields[j=0]; j < fields.length; field=fields[++j]){
                    if(fields[j]=="state"){
                        var state = ["start_date", "due_date", "due_date", "validation", "validation"];
                        for(var k = 0; k < state.length; k++){
                            if(task.fields.state == k){
                                if(task.fields[state[k]])
                                    task.fields["due_date"] = ""+task.fields[state[k]];
                                else
                                    task.fields["due_date"] = "-"; 
                            }
                        }
                        var state_for_percentage = task.fields.state;
                        task.fields[field] = gettext("State"+task.fields[field]);
                        if(state_for_percentage == 2) task.fields[field] += " "+task.fields.progress+"%";
                    };
                    if(fields[j]=="offer")task.fields[field] += " €";
                    if(fields[j]=="target_name"){if(!task.fields[field]) {task.fields[field]="-";}; };
                    line.appendChild(document.createElement('td')).innerHTML = "<a href=/prjmgt/"+task.pk+"/view/"+views[j]+">"+task.fields[field]+"</a>";
                }
                document.getElementById('dynamicTableOverview').appendChild(line);
            }
            paginateOverviewTable(projectid, paginator, nbpage);
        }
    );
}

function getGithubRepos(id, login, repo) {
    OIajaxCall("/project/"+id+"/getgithubrepos", null, "output", function(response){
            output.innerHTML="";
            repos = eval(response)
            for(login in repos) github_login.add(new Option(login));
            github_login.value = login;
            updateGithubRepos();
            github_repo.value = repo;
            show('github_form');
        });
}
function updateGithubRepos() {
    github_repo.options.length=0;
    var i=0;
    for(repo=repos[github_login.value][i]; i<repos[github_login.value].length; repo=repos[github_login.value][++i])
        github_repo.add(new Option(repo));
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
            }
        );  
}
function prepareText(divid){
    var allvalue = "<dl>";
    allvalue += "<dt><b>"+gettext("What I did:")+"</b></dt><dd>"+document.getElementById("bug_report_"+divid+"_1").value+"</dd>";
    allvalue += "<dt><b>"+gettext("What happened:")+"</b></dt><dd>"+document.getElementById("bug_report_"+divid+"_2").value+"</dd>";
    allvalue += "<dt><b>"+gettext("What should happen:")+"</b></dt><dd>"+document.getElementById("bug_report_"+divid+"_3").value+"</dd>";
    allvalue += "<dt><b>"+gettext("Environment:")+"</b></dt><dd>"+document.getElementById("bug_report_"+divid+"_4").value+"</dd>";
    
    document.getElementById("text_"+divid).value = allvalue.replace(/\n/g,"<br />")+"</dl>";
}
function buildText(divid){
    for(var i = 1; i <= 4; ++i){
        var dd = document.getElementById("text_"+divid).getElementsByTagName("dd")[i-1];
        if(dd) document.getElementById("bug_report_"+divid+"_"+i).innerHTML = dd.innerHTML.replace(/<br( \/)*>/g, "\n");
    }
}
function saveSpec(divid, projectid, order, specid, lang, callBack) {
    tinymce.remove('#text_'+divid);
    var params = "text="+encodeURIComponent(getValue("text_"+divid)) + "&order="+order + "&type="+getValue("type_"+divid);
    if(lang != null) params +="&language="+lang;
    if(getValue("url_"+divid)) params+="&url="+encodeURIComponent(getValue("url_"+divid));
    if(getValue("filename_"+divid)) params+="&filename="+getValue("filename_"+divid);
    if(getValue("ts_"+divid)) params+="&ts="+getValue("ts_"+divid);
    if(getValue("image_"+divid)) params+="&image="+getValue("image_"+divid);
    OIajaxCall("/project/"+projectid+"/savespec/"+specid, params, divid, 
        function(){
            var div = document.getElementById(divid);
            var length = div.getElementsByTagName("input").length;
            var specorder =  div.getElementsByTagName("input")[length-1].value;
            div.id="spec_"+projectid+"_"+specorder;
            div.className = "cleared";
            div.style.position = "relative";
            if(document.getElementById("sepspec_"+projectid)) 
                div.parentNode.removeChild(document.getElementById("sepspec_"+projectid));
            if(callBack) callBack();
        }
    );
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
function OISpot(specDiv, projectid, specid, spotid, x, y, title, linkid, number, color) {
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
    this.number.style.background = color || "#0094B5";
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
    if(this.linkid) OIajaxCall(prjsite+'/prjmgt/'+this.linkid+'/summarize', null, this.div.id);
}
OISpot.prototype.saveTask = function saveTaskSpot() {
    addTask(encodeURIComponent(this.div.getElementsByClassName("newtask_title")[0].value), this.projectid, null, makeObjectCallback(this.save, this));
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
            oiTree.deleteNode(this.linkid);
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
