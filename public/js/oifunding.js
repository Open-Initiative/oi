function featureShowHide (divid){
    var featureid_block = ["features_0", "features_3", "features_4"];
    var featureid_blockHeadid = ["featureid_proposed", "featureid_progress", "featureid_finish"];
    for(var i = 0; i < featureid_block.length; i++){
        if(featureid_block[i]){
            if(divid == featureid_block[i]){
                if(document.getElementById(divid).style.display == "none") $("#"+divid).slideDown();
                if(document.getElementById(featureid_blockHeadid[i]).style.backgroundColor != "#1E9947") document.getElementById(featureid_blockHeadid[i]).style.backgroundColor = "#1E9947";
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
function seeMore(divid1, divid2){
    if(document.getElementById(divid1) && document.getElementById(divid2)){
        if(document.getElementById(divid1).className == "invisible" && document.getElementById(divid2).className == ""){
            document.getElementById(divid1).className = "";
            document.getElementById(divid2).className = "invisible"
        }else{
            document.getElementById(divid2).className = "";
            document.getElementById(divid1).className = "invisible"
        }
    }
}
function popup(){
    document.getElementById("flou").style.width = document.getElementsByTagName("body")[0].scrollWidth+"px";
    document.getElementById("flou").style.height = document.getElementsByTagName("body")[0].scrollHeight+"px";
    document.getElementById("flou").style.top = "0px";
    document.getElementById("flou").style.left = "0px";
}
function noPopup(){
    document.getElementById("flou").style.width = "0px";
    document.getElementById("flou").style.height = "0px";
//    document.getElementById("flou").style.top = "0px";
//    document.getElementById("flou").style.left = "0px";
}
