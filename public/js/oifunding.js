function featureShowHide (divid){
    var featureid_block = ["features_0", "features_3", "features_4"];
    var featureid_blockHeadid = ["featureid_proposed", "featureid_progress", "featureid_finish"];
    for(var i = 0; i < featureid_block.length; i++){
        if(featureid_block[i]){
            if(divid == featureid_block[i]){
                if(document.getElementById(divid).style.display == "none") $("#"+divid).slideDown();
                if(document.getElementById(featureid_blockHeadid[i]) && document.getElementById(featureid_blockHeadid[i]).style.backgroundColor != "#1E9947") document.getElementById(featureid_blockHeadid[i]).style.backgroundColor = "#1E9947";
            }else{
                if(document.getElementById(featureid_blockHeadid[i]) && document.getElementById(featureid_blockHeadid[i]).style.backgroundColor != "#0094B5") document.getElementById(featureid_blockHeadid[i]).style.backgroundColor = "#0094B5";
                if(document.getElementById(featureid_block[i])) $("#"+featureid_block[i]).slideUp();
            }
        }
    }
}

function deleteFeature(projectid) {
    if(confirm(gettext("Are you sure you want to delete this task permanently?"))) {
        OIajaxCall("/project/delete/"+projectid, null, "output",
            function(){
                var feature = document.getElementById("featureDiv_"+projectid);
                if(feature) feature.parentNode.removeChild(feature);
        });
    }
}
function visibleFeature(projectid){
    OIajaxCall('/project/'+projectid+'/setpublic', 'read='+document.getElementById('public_read_'+projectid).checked, 'output', 
        function(){
            if(!document.getElementById('public_read_'+projectid).checked){
                document.getElementById("featureDiv_"+projectid).style.opacity = 0.4;
            }else{
               document.getElementById("featureDiv_"+projectid).style.opacity = 1; 
            }
        }
    );
}
function checkSavedSpecs(projectid){
    if(nbspec==nbSavedSpecs)
        (hasChild > 0?document.location.href="/funding/"+projectid:document.location.href="/funding/"+projectid+"/manage");
}
function saveAllSpec(projectid){
    var specid = document.getElementsByName("specid");
    var specorder = document.getElementsByName("specorder");
    var speclang = document.getElementsByName("speclang");
    nbspec = 0; nbSavedSpecs = 0;
    for (var i = 0; i < specid.length; i++){
        if(specorder[i].value == 3) tinyMCE.execCommand('mceRemoveControl', false, "text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value)
        var existTextValue = document.getElementById("text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value).value;
        if(specorder[i].value == 1 || existTextValue && existTextValue != ""){
            nbspec++;
            saveSpec(projectid+"_"+specorder[i].value+"_"+speclang[i].value, projectid, specorder[i].value, specid[i].value, speclang[i].value, "funding");
        }
    }
    checkSavedSpecs(projectid);
}
function seeMore(dividblock1, dividblock2){
    $('#'+dividblock1).toggle();
    $('#'+dividblock2).delay(100).fadeToggle();
}
function selectplugin(projectid, plugintype) {
    if(plugintype == "big"){
        var width = "270px";
        var height = "310px";
    }else if(plugintype == "small"){
        var width = "240px";
        var height = "99px";
    }else{
        var width = "102px";
        var height = "42px";
    }
    var iframe = "<iframe style='border:none' width='"+width+"' height='"+height+"' src='http://"+sites["Open Funding"]+"/funding/"+projectid+"/embed?type="+plugintype+"'></iframe>";
    document.getElementById('plugincode').value = iframe;
    document.getElementById('plugin_preview').innerHTML = iframe;
}
