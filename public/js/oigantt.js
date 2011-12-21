var one_day = 1000*60*60*24;
var row_height = 13;

function GanttBar(gantt) {
    this.gantt = gantt;
//    this.id = id;
//    this.parent = this.gantt.bars[parentid];
//    this.children = [];
//    if(parentid) this.parent.children.push(this);
}
GanttBar.prototype.addPeriod = function(bardiv, begin, end, color) {
    div = document.getElementById(newDiv(this.bardiv.id));
    div.style.width = ((end - begin) / one_day * this.gantt.daywidth) + "px";
    div.style.cssFloat = "left";
    div.style.height = "10px";
    div.style.background = color;
    return div;
}
GanttBar.prototype.draw = function() {
    this.bardiv = document.getElementById(newDiv(this.gantt.div.id));
    this.bardiv.style.position = "absolute";
    this.bardiv.style.left = ((this.creationDate - this.gantt.startDate) / one_day * this.gantt.daywidth) + "px";
    this.bardiv.style.top = (this.gantt.bars.indexOf(this) * row_height + 20) + "px";
    this.bardiv.style.width = ((this.validationDate - this.deliverDate) / one_day * this.gantt.daywidth) + "px";
    
    this.addPeriod(this.bardiv, this.creationDate, this.startDate, "red");
    this.addPeriod(this.bardiv, this.startDate, this.deliverDate, "blue");
    this.addPeriod(this.bardiv, this.deliverDate, this.validationDate, "green");
}
GanttBar.prototype.setDates = function(dates) {
    this.creationDate = dates[0];
    this.startDate = dates[1];
    this.deliverDate = dates[2];
    this.validationDate =dates[3];
    this.draw();
}

function OIGantt(divid, startDate, endDate) {
    this.startDate = startDate;
    this.endDate = endDate;
    this.height = 100;
    this.daywidth = 12;
    this.bars = [];
    this.barids = {};
    
    this.div = document.getElementById(divid);
    this.div.style.height = this.height+20+"px";
    this.div.style.border = "solid black 1px";
    this.div.style.overflow = "auto";
    this.div.style.position = "relative";
    
    this.drawTimeline();
}
OIGantt.prototype.drawTimeline = function() {
    this.div.innerHTML = '<div style="height:20px;width:'+(this.daywidth*80)+'px">'+this.startDate.getMonth()+'</div>';
    last = new Date(this.startDate);
    last.setDate(this.startDate.getDate()+80);
    for(var day = new Date(this.startDate); day<last; day.setDate(day.getDate()+1)) {
        if(day.getDate()==1) this.div.innerHTML += '<div style="float: left;position: relative;top: -20px;width:0">'+day.getMonth()+'</div>';
        this.div.innerHTML += '<div style="width:'+(this.daywidth-1)+'px;height:'+this.height+'px;border-right:solid gray 1px;float:left">'+day.getDate()+'</div>';
    }
}
OIGantt.prototype.addBar = function(id, dates, after) {
    var newBar = new GanttBar(this)
    this.bars.splice(after, 0, newBar);
    this.barids[id] = newBar;
    newBar.setDates(dates);
}
OIGantt.prototype.addSpace = function(after) {

}
