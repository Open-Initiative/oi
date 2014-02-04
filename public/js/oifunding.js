function allFeatureFunction(){
//  gather all the feature function and call it in the template
    isFeatureState();
    notVisibleBtnFeature();
    oneBtnFeatureToHide();
    showFeatureState();
}
function featureShowHide (divid){
    var featureid_block = ["features_0", "features_3", "features_4"];
    var featureid_blockHeadid = ["featureid_proposed", "featureid_progress", "featureid_finished"];
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
function showFeatureState(){
//  make a featureShowHide if the state btn is visible
    var featureid_block = ["features_0", "features_3", "features_4"];
    var featureid_blockHeadid = ["featureid_proposed", "featureid_progress", "featureid_finished"];
    for(var i = 0; i < featureid_blockHeadid.length; i++){
        if(document.getElementById(featureid_blockHeadid[i]) && document.getElementById(featureid_blockHeadid[i]).style.display != "none"){
            featureShowHide(featureid_block[i]);
            break;
        }
    }

}
function isFeatureState(){
//  if button exist, show the button state 
    if(document.getElementById("featureid_proposed") && (document.getElementById("featureid_progress")||document.getElementById("featureid_finished"))){
        show('featureid_proposed');
    }
    if(document.getElementById("featureid_progress") && (document.getElementById("featureid_finished")||document.getElementById("featureid_proposed"))){
        show('featureid_progress');
    }
    if(document.getElementById("featureid_finished") && (document.getElementById("featureid_proposed")||document.getElementById("featureid_progress"))){
        show('featureid_finished');
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
function notVisibleBtnFeature(){
//  for visiters hide feature btn if all the features is hide
    var featureid_block = ["features_0", "features_3", "features_4"];
    var featureid_blockHeadid = ["featureid_proposed", "featureid_progress", "featureid_finished"];
    for(var i = 0; i < featureid_block.length; i++){
        if(document.getElementById(featureid_block[i]) && !document.getElementById(featureid_block[i]).getElementsByClassName("featureblock").length){
            if(document.getElementById(featureid_blockHeadid[i])) hide(featureid_blockHeadid[i]);
        }
    }
}
function oneBtnFeatureToHide(){
//  if there are just one btn visible, hide it
    if(document.getElementById("featureid_blockHead")){
        var btns = document.getElementById("featureid_blockHead").getElementsByClassName('statebtn');
        var cpt_btn_hide = 0;
        for (var i = 0; i < btns.length; i++){
            if(btns[i].style.display == "none")
                cpt_btn_hide++;
        }
        if(cpt_btn_hide > 1)
            hide("featureid_blockHead");
    }
}
function checkSavedSpecs(projectid){
    document.location.href="/funding/"+projectid;
}
function specsToSave(projectid){
    var nbSpecToSave = 0;
    var specid = document.getElementsByName("specid");
    var specorder = document.getElementsByName("specorder");
    var speclang = document.getElementsByName("speclang");
    var file_value = document.getElementById("file_"+projectid+"_1_").value;
    for (var i = 0; i < specid.length; i++){
        if(specorder[i].value == 3) tinymce.remove("#text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value);
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
    var file_value = document.getElementById("file_"+projectid+"_1_").value;
    nbspec = 0;
    for (var i = 0; i < specid.length; i++){
        if(specorder[i].value == 3) tinymce.remove("#text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value);
        var existTextValue = document.getElementById("text_"+projectid+"_"+specorder[i].value+"_"+speclang[i].value).value;
        if(specorder[i].value == 1 && file_value || existTextValue && existTextValue != ""){
            saveSpec(projectid+"_"+specorder[i].value+"_"+speclang[i].value, projectid, specorder[i].value, specid[i].value, speclang[i].value, function(){
                if(++nbspec == nbSpecToSave) checkSavedSpecs(projectid);
            });
        }
    }
}
function sortFeature(projectid){
    jQuery(".features_manage").sortable({containment: "parent", update: function(event,ui){
        var params = jQuery(this).sortable("toArray").map(function(id,index) {return id+"="+index}).join("&");
        OIajaxCall("/project/"+projectid+"/sort", params, "output");
    }});
}
function seeMore(dividblock1, dividblock2){
    //hide one div and show the other
    $('#'+dividblock1).toggle();
    $('#'+dividblock2).delay(100).fadeToggle();
}
function shrinkAllFeatures(){
    //hide all feature block
    $('.featuredetailspec').hide();
    $('.coverfeature').show();
    $('.see-less').hide();
    $('.see-more').show();
}
function expandFeature(taskid){
    //if the hash is equal to the taskid, show the feature block or hide it
    shrinkAllFeatures();
    if(document.location.hash == "#feature_"+taskid){
        hide('specs_'+taskid);
        show('specs_'+taskid+'_hide');
        show('see_more_'+taskid);
        hide('see_less_'+taskid);
        document.location.hash = "x";
    }else if(document.location.hash != "#feature_"+taskid){
        show('specs_'+taskid);
        hide('specs_'+taskid+'_hide');
        hide('see_more_'+taskid);
        show('see_less_'+taskid);
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
function updateStockReward(projectid, rewardid, moreOrLess){
    if(moreOrLess) var nb = 1; else var nb = -1;
    OIajaxCall("/project/"+projectid+"/updatestockreward/"+rewardid, "update="+nb, "output", function(){
        var oldvalue = parseInt(document.getElementById("nb_reward_"+rewardid).innerHTML);
        if((oldvalue >= 1)||(moreOrLess && oldvalue == 0))
            document.getElementById("nb_reward_"+rewardid).innerHTML = oldvalue + nb;
    })
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
function completeTask(projectid, taskid){
    OIajaxCall("/project/"+projectid+"/completetask/"+taskid, null, "output");
}
function hideRelated(){
    if(document.getElementById('pite').className!='pite'){
        $( "#pite" ).animate({"right": "+=250px"}, 3000, function() {
            $("#pite").css( "overflow", "visible" );
            $("#pite").addClass("pite");
        });
    }else{
        $("#pite").css( "overflow", "hidden" );
        $( "#pite" ).animate({"right": "-=250px"}, 3000, function() {
            $("#pite").removeClass("pite");
        });
    }
}
