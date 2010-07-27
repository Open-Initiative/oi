function OIajaxCall(url, params, divid) {
    xmlhttp = new XMLHttpRequest();
    if(params==null) {
        method="GET";
    } else {
        method="POST";
    }
    xmlhttp.open(method,url,false);
    xmlhttp.send(params);
    document.getElementById(divid).innerHTML=xmlhttp.responseText;
}
function getValue(eltid){
    elt = document.getElementById(eltid);
    if(elt==null) return null;
    return elt.value.replace(/%/g,"%25").replace(/&/g,"%26").replace(/;/g,"%3B");
}
function newDiv(parentid) {
    divid = "oi"+((new Date).getTime());
    document.getElementById(parentid).innerHTML+='<div id="'+divid+'"></div>';
    return divid;
}
