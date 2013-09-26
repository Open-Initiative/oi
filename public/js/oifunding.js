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
    document.location.href="/funding/"+projectid;
}
function specsToSave(projectid){
    var nbSpecToSave = 0;
    var specid = document.getElementsByName("specid");
    var specorder = document.getElementsByName("specorder");
    var speclang = document.getElementsByName("speclang");
    var file_value = document.getElementById("file_"+projectid+"_1_None").value;
    for (var i = 0; i < specid.length; i++){
        if(specorder[i].value == 3) tinyMCE.execCommand('mceRemoveControl', false, "text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value)
        var existTextValue = document.getElementById("text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value).value;
        if(specorder[i].value == 1 && file_value || existTextValue && existTextValue != ""){
            nbSpecToSave ++; 
        }
    }
    if(nbSpecToSave != 0){
        saveAllSpec(projectid, nbSpecToSave);
    }else{
        checkSavedSpecs(projectid);
    }
}
function saveAllSpec(projectid, nbSpecToSave){
    var specid = document.getElementsByName("specid");
    var specorder = document.getElementsByName("specorder");
    var speclang = document.getElementsByName("speclang");
    var file_value = document.getElementById("file_"+projectid+"_1_None").value;
    nbspec = 0;
    for (var i = 0; i < specid.length; i++){
        if(specorder[i].value == 3) tinyMCE.execCommand('mceRemoveControl', false, "text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value)
        var existTextValue = document.getElementById("text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value).value;
        if(specorder[i].value == 1 && file_value || existTextValue && existTextValue != ""){
            saveSpec(projectid+"_"+specorder[i].value+"_"+speclang[i].value, projectid, specorder[i].value, specid[i].value, speclang[i].value, function(){
                if(++nbspec == nbSpecToSave) checkSavedSpecs(projectid);
            });
        }
    }
}
function seeMore(dividblock1, dividblock2){
    //hide one div and show the other
    $('#'+dividblock1).toggle();
    $('#'+dividblock2).delay(100).fadeToggle();
}
function reset(taskid){
    //hide all feature block
    $('.featuredetailspec').hide();
    $('.no-see-more').hide();
    $('.see-more').show();
}
function urlFeature(taskid){
    //if the hash is equal to the taskid, show the feature block or hide it
    reset();
    if(document.location.hash == "#feature_"+taskid){
        hide('featuredesc_'+taskid);
        show('featuredesc_'+taskid+'_hide');
        show('see_more_'+taskid);
        hide('no_see_more_'+taskid);
        document.location.hash = "x";
    }else if(document.location.hash != "#feature_"+taskid){
        show('featuredesc_'+taskid);
        hide('featuredesc_'+taskid+'_hide');
        hide('see_more_'+taskid);
        show('no_see_more_'+taskid);
        document.location.hash = "feature_"+taskid;
    }
}
function selectplugin(projectid, plugintype) {
    if(plugintype == "big"){
        var width = "300px";
        var height = "400px";
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
function deleteReward(projectid, rewardid){
    if(confirm(gettext("Are you sure you want to delete this reward permanently?"))) {
        OIajaxCall("/project/"+projectid+"/deletereward/"+rewardid, null, "output", 
        function(){
            var rewardblock = document.getElementById("blockreward_"+rewardid);
            var linereward = document.getElementById('reward_bottom_line_'+rewardid);
            rewardblock.parentNode.removeChild(rewardblock);
            linereward.parentNode.removeChild(linereward);
        })
    }
}
