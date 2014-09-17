function addSpec(projectid) {
    var divid = newDiv("specs_"+projectid);
    OIajaxCall(prjsite+"/prjmgt/"+projectid+"/editspec/0?divid="+divid+"&specorder=-1", null, divid, 
        function(){changeSpecType(divid, 1);});
        document.getElementById(divid).scrollIntoView();
}
function editSpec(projectid, specorder, type) {
    var specid = getValue("specid_"+projectid+"_"+specorder);
    var divid = "spec_"+projectid+"_"+specorder;
    OIajaxCall(prjsite+"/prjmgt/"+projectid+"/editspec/"+specid+"?divid="+divid, null, divid,
        function(){changeSpecType(divid, type);});
}
function changeSpecType(divid, type) {
    if(getValue("type_"+divid)==1)tinymce.remove('#text_'+divid);
    var text = getValue("text_"+divid);
    var projectid = getValue("projectid_"+divid);
    var specid = getValue("specid_"+divid);
    document.getElementById("type"+getValue("type_"+divid)+"_"+divid).className = "spectype";
    document.getElementById("type"+type+"_"+divid).className = "spectype spectypeselected";
    document.getElementById("type_"+divid).value = type;
    var url = prjsite+"/prjmgt/"+projectid+"/editspecdetails/"+specid+"?divid="+divid+"&type="+type+"&ts="+(new Date()).getTime();
    OIajaxCall(url, null, "spec_"+divid, 
        function(){
            if(getValue("type_"+divid)==6) buildText(divid);
            if(getValue("type_"+divid)==1){
                var ed = new tinymce.Editor('text_'+divid, objectInitTinyMce, tinymce.EditorManager);
                ed.render();
            }
        });
}
