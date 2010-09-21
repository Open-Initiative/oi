function addExperience() {
    divid = newDiv("experience");
    OIajaxCall("/user/editexperience/0", null, divid);
}
function addTraining() {
    divid = newDiv("training");
    OIajaxCall("/user/edittraining/0", null, divid);
}
function addContact(userid) {
    OIajaxCall("/user/invite/"+userid, null, "output");
}
function writeMP(userid) {
    OIajaxCall("/user/writemp/"+userid, null, "sendmp");
}
function sendMP(userid) {
    OIajaxCall("/user/sendmp/"+userid, "message="+getValue("MPmessage")+"&subject="+getValue("MPsubject"), "sendmp");
}
