var one_day = 1000*60*60*24;

function GanttBar(gantt) {
    this.gantt = gantt;
    this.bardiv = document.getElementById(newDiv(this.gantt.div.id));
}
GanttBar.prototype.addPhase = function(bardiv, begin, end, className) {
    div = document.getElementById(newDiv(this.bardiv.id));
    div.style.width = ((end - begin) / this.gantt.scale) + "px";
    div.className = className;
    return div;
}
GanttBar.prototype.draw = function() {
    if(this.bardiv) this.gantt.div.removeChild(this.bardiv);
    this.bardiv = document.getElementById(newDiv(this.gantt.div.id));
    this.bardiv.style.position = "absolute";
    this.bardiv.style.left = ((this.creationDate - this.gantt.startDate) / this.gantt.scale) + "px";
    this.bardiv.style.top = (this.gantt.bars.indexOf(this) * this.gantt.rowHeight + this.gantt.headerHeight) + "px";
    this.bardiv.style.width = ((this.deliverDate - this.creationDate) / this.gantt.scale) + "px";
    
    this.addPhase(this.bardiv, this.creationDate, this.startDate, "ganttbar1");
    this.addPhase(this.bardiv, this.startDate, this.deliverDate, "ganttbar2");
    this.addPhase(this.bardiv, this.deliverDate, this.validationDate, "ganttbar3");
}
GanttBar.prototype.setDates = function(dates) {
    this.creationDate = dates[0];
    this.startDate = dates[1];
    this.deliverDate = dates[2];
    this.validationDate =dates[3];
}

function OIGantt(divid, startDate, endDate) {
    this.periods = [1000*60*5, 1000*60*60, 1000*60*60*24, 1000*60*60*24*7, "month", "year"];
    this.scale = 1000*60*60;
    this.period = 1000*60*60*24;
    this.rowHeight = 20;
    this.headerHeight = 35;

    this.div = document.getElementById(divid);
    this.header = document.getElementById(newDiv(divid));
    this.graph = document.getElementById(newDiv(divid));
    this.header.style.height = this.headerHeight + "px";
    
    this.startDate = startDate || new Date();
    this.endDate = new Date(Math.max(endDate, new Date(this.scale*this.div.style.width+(this.startDate.getTime()))));;
    this.bars = [];
    this.barids = {};
    
    this.drawTimeline();
}
OIGantt.prototype.drawTimeline = function() {
    this.header.innerHTML = this.startDate.getMonth()+"";
    this.graph.style.width = (this.endDate - this.startDate + this.period) / this.scale+"px";
    
    for(var day = new Date(this.startDate); day<this.endDate; day.setDate(day.getDate()+1)) {
        if(day.getDate()==1) this.graph.innerHTML += '<div style="float: left;position: relative;top: -'+this.headerHeight+'px;width:0">'+day.getMonth()+'</div>';
        this.graph.innerHTML += '<div style="width:'+(one_day/this.scale-1)+'px" class="ganttperiod">'+day.getDate()+'</div>';
    }
}
OIGantt.prototype.redraw = function(barNb) {
    this.graph.style.height = (this.rowHeight * this.bars.length + this.headerHeight)+"px";
    if(!barNb || barNb==-1) barNb = 0;
    for(var i=barNb||0; i<this.bars.length; i++) 
        if(this.bars[i]) this.bars[i].draw();
}
OIGantt.prototype.addBar = function(id, dates, afterid) {
    var newBar = new GanttBar(this)
    var afterNb = this.bars.indexOf(this.barids[afterid])
    this.bars.splice(afterNb+1, 0, newBar);
    this.barids[id] = newBar;
    newBar.setDates(dates);
}
OIGantt.prototype.addSpace = function(afterid) {
    pos = this.bars.indexOf(this.barids[afterid]) + 1;
    this.bars.splice(pos, 0, null);
}
OIGantt.prototype.hideBar = function(id, nbnext) {
    bar = this.barids[id];
    pos = this.bars.indexOf(bar);
    this.div.removeChild(bar.bardiv);
    bar.bardiv = null;
    this.bars.splice(pos, 1 + nbnext);
}
OIGantt.prototype.showBar = function(id, afterid) {
    pos = this.bars.indexOf(this.barids[afterid]) + 1;
    this.bars.splice(pos, 0, this.barids[id]);
}
OIGantt.prototype.highlight = function(id) {
    this.barids[id].bardiv.className = "gantthighlight";
}
OIGantt.prototype.unhighlight = function(id) {
    this.barids[id].bardiv.className = "";
}
