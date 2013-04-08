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
