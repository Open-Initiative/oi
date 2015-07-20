function addTask(tasktitle, projectid, offer, callBack) {
    var params = "title="+tasktitle+"&inline=1&progress=0";
    if(offer) params += "&offer="+offer; 
    if(projectid) params += "&parent="+projectid;
    if(document.getElementById("appname")) params += "&app="+getValue("appname");
    OIajaxCall("/project/save/0", params, null, 
        function(response){
            var task = eval(response)[0];
            if(callBack) callBack(task.pk);
        }); 
}
function submitProject(){
    $('#projects').fadeToggle(); $('#newproject').fadeToggle();
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
function cancelBid(projectid, started) {
    question = gettext("Are you sure you want to cancel your bid?");
    if(started) question += gettext(" You will be reimbursed if the project assignee accepts the cancellation. The commission stays at your expense.");
    if(confirm(question))
        OIajaxCall("/project/cancelbid/"+projectid, null, "output");
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
function deltmp(projectid,filename,ts,divid) {
    OIajaxCall("/project/"+projectid+"/deltmp", "filename="+filename+"&ts="+ts+"&divid="+divid, "output", 
        function(){changeFile(divid);});
}

function changeFile(divid) {
    document.getElementById("filediv_"+divid).style.display="inline";
    document.getElementById("filespan_"+divid).style.display="none";
}
