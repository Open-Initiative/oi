function allFeatureFunction(){
//  gather all the feature function and call it in the template
    isFeatureState();
    notVisibleBtnFeature();
    oneBtnFeatureToHide();
    project_content('featuresproject');
    project_oncload_page();
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
        var width = "350px";
        var height = "450px";
    }else if(plugintype == "small"){
        var height = "99px";
        var width = "240px";
    }else if(plugintype == "tiny"){
        var height = "42px";
        var width = "105px";
    }else{
        var height = "170px";
        var width = "350px";
    }
    var iframe = "<iframe id='widget_"+projectid+"_"+plugintype+"' style='border:none; width:"+width+"; height: "+height+"; max-width: 350px;' src='http://"+sites["Open Funding"]+"/funding/"+projectid+"/embed?type="+plugintype+"'></iframe>";

    //Popup for tiny plugin
    if(plugintype=='tiny') {
        iframe += '<iframe id="tinypopup" class="of_'+projectid+'_iframe_tiny" style="display:none;border:none;position:absolute;width:430px;height:200px;" src="http://'+sites["Open Funding"]+'/funding/'+projectid+'/embed_popup" onmouseout="hideOFWidgetPopup()" onmouseover="clearTimeout(oftimer);"></iframe><script>function hideOFWidgetPopup() {oftimer = setTimeout(function(){document.getElementById("tinypopup").style.display = "none";},3000);} oftimer=""; var widget=document.getElementById("widget_'+projectid+'_tiny");widget.onmouseout=hideOFWidgetPopup;widget.onmouseover=function() {document.getElementById("tinypopup").style.display = "block"; clearTimeout(oftimer);}</script>';
    }
    document.getElementById('plugincode').value = iframe;
    document.getElementById('plugin_preview').innerHTML = iframe;
    
    //for preview
    if(plugintype=='tiny') {
        oftimer="";
         var widget=document.getElementById("widget_"+projectid+"_tiny");
         widget.onmouseout=hideOFWidgetPopup;
         widget.onmouseover=function() {
            document.getElementById('tinypopup').style.display = 'block';
            clearTimeout(oftimer);
        }
    }
}
//For preview
function hideOFWidgetPopup() {
    oftimer = setTimeout(function(){document.getElementById('tinypopup').style.display = 'none';},3000);
}
function updateStockReward(projectid, rewardid, moreOrLess){
    //deals with the stock of reward
    if(moreOrLess) var nb = 1; else var nb = -1;
    OIajaxCall("/project/"+projectid+"/updatestockreward/"+rewardid, "update="+nb, "output", function(){
        var oldvalue = parseInt(document.getElementById("nb_reward_"+rewardid).innerHTML);
        if((oldvalue >= 1)||(moreOrLess && oldvalue == 0))
            document.getElementById("nb_reward_"+rewardid).innerHTML = oldvalue + nb;
    })
}
function deleteReward(projectid, rewardid){
    //delete reward
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
function checkConfirmation(projectid){
    //check if exist value before send it by the form
    var form_valid = document.getElementById('simple_sum_'+projectid).value != '';
    if(!form_valid){
        document.getElementById('output').innerHTML = gettext("Please indicate the amount");
        return false;
    }
    return true;
}
function confirmBid(projectid) {
    //get the feature or project id and make a bid on it
    OIajaxCall("/project/confirmbid/"+$("input[name='order']:checked").val(), "bid="+getValue("bid_"+projectid), "output");
}
function completeTask(projectid, taskid){
    //complete the feature with project bid
    OIajaxCall("/project/"+projectid+"/completetask/"+taskid, null, "output");
}
function arrow_Up_Down(divid){
    $('#'+divid).toggle();//show or hide the menu
    $('#arrow_header_up').toggle();//change arrow if the menu is visible or not
    $('#arrow_header').toggle();
}
function project_content(divid){
    //show the content of feature, community or discussion
    var tabs_Headid = ["features", "community", "discussions"];
    var tabs_blockid = ["featuresproject", "communityproject", "discussionsproject"];
    for(var i = 0; i < tabs_Headid.length; i++){
        if(divid == tabs_blockid[i]){
            $("#"+tabs_Headid[i]).addClass('tab_project_selected');
            $("#"+tabs_blockid[i]).removeClass('invisible');
        }else{
            $("#"+tabs_Headid[i]).removeClass('tab_project_selected');
            $("#"+tabs_blockid[i]).addClass('invisible');
        }
    }
}
function project_oncload_page(){
    //on project page, chose which part to show
    if(document.location.hash == "#features") project_content('featuresproject');
    else if (document.location.hash == "#community") project_content('communityproject');
    else if(document.location.hash == "#discussions") project_content('discussionsproject');
}
function openPanel(){
    //open related panel, it appear when the screen is small
    $('#shrinkrelated').animate({'width': '265px'}, 300);
    $('#btn_extend_close').removeClass('invisible');
    $('#btn_extend_open').addClass('invisible');
}
function closePanel(){
    //close related panel, it appear when the screen is small
    document.getElementById('shrinkrelated').style.cssText='';
    $('#btn_extend_open').removeClass('invisible');
    $('#btn_extend_close').addClass('invisible');
}
function initSwipePanel(){
    //init the window with this params
    var panel = document.getElementById('shrinkrelated');
    if (window.matchMedia("(max-width: 750px)").matches) {
        Hammer(panel).on("swipeleft dragleft", openPanel);
        Hammer(panel).on("swiperight dragright", closePanel);
    }
}
function resizeSwipePanelEffect(){
    //if window resize, do this effect
    $(window).resize(function() {
        if (window.matchMedia("(max-width: 750px)").matches) {
            initSwipePanel();
        }else{
            var panel = document.getElementById('shrinkrelated');
            Hammer(panel).off("swipeleft dragleft", openPanel);
            Hammer(panel).off("swiperight dragright", closePanel);
        }
    });
}
function addSpec(projectid) {
    var divid = newDiv("specs_"+projectid);
    OIajaxCall(prjsite+"/funding/"+projectid+"/editspec/0?divid="+divid+"&specorder=-1", null, divid, 
        function(){changeSpecType(divid, 1);});
        document.getElementById(divid).scrollIntoView();
}
function editSpec(projectid, specorder, type) {
    var specid = getValue("specid_"+projectid+"_"+specorder);
    var divid = "spec_"+projectid+"_"+specorder;
    OIajaxCall(prjsite+"/funding/"+projectid+"/editspec/"+specid+"?divid="+divid, null, divid,
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
    var url = prjsite+"/funding/"+projectid+"/editspecdetails/"+specid+"?divid="+divid+"&type="+type+"&ts="+(new Date()).getTime();
    OIajaxCall(url, null, "spec_"+divid, 
        function(){
            if(getValue("type_"+divid)==6) buildText(divid);
            if(getValue("type_"+divid)==1){
                var ed = new tinymce.Editor('text_'+divid, objectInitTinyMce, tinymce.EditorManager);
                ed.render();
            }
        });
}


