var one_day = 1000*60*60*24;

function GanttBar(gantt, dates, bgClass) {
    this.gantt = gantt;
    this.bardiv = null;
    this.bgdiv = null;
    this.bgClass = bgClass;
    this.dates = dates;
}
GanttBar.prototype.addPhase = function(bardiv, begin, end, className) {
    var div = document.getElementById(newDiv(this.bardiv.id));
    div.style.width = ((end - begin) / this.gantt.scale) + "px";
    div.className = className;
    return div;
}
GanttBar.prototype.draw = function() {
    if(this.bgdiv) this.gantt.div.removeChild(this.bgdiv);
    if(this.bardiv) this.gantt.div.removeChild(this.bardiv);
    
    this.bgdiv = document.createElement("div");
    this.bgdiv.style.position = "absolute";
    this.bgdiv.style.top = (this.gantt.bars.indexOf(this) * this.gantt.rowHeight + this.gantt.headerHeight) + "px";
    this.bgdiv.style.height = this.gantt.rowHeight + "px";
    this.bgdiv.className = "ganttbg"+this.bgClass;
    this.gantt.div.appendChild(this.bgdiv);
    
    if(this.dates.length) {
        this.bardiv = document.getElementById(newDiv(this.gantt.div.id));
        this.bardiv.style.position = "absolute";
        this.bardiv.style.left = ((this.dates[0] - this.gantt.startDate) / this.gantt.scale) + "px";
        this.bardiv.style.top = (this.gantt.bars.indexOf(this) * this.gantt.rowHeight + this.gantt.headerHeight) + "px";
        this.bardiv.style.width = ((this.deliverDate - this.creationDate) / this.gantt.scale) + "px";
        
        var i;
        for(i=0; i < this.dates.length-1; i++)
            this.addPhase(this.bardiv, this.dates[i], this.dates[i+1], "ganttbar"+(i+1));
    }
}

function OIGantt(divid, startDate, endDate) {
    this.periods = [1000*60*5, 1000*60*60, 1000*60*60*24, 1000*60*60*24*7, "month", "year"];
    this.scale = 1000*60*60;
    this.period = 1000*60*60*24;
    this.rowHeight = 20;
    this.headerHeight = 20;
    
    parentdiv = document.getElementById(divid);
    this.startDate = startDate || new Date();
    this.endDate = new Date(Math.max(endDate, new Date(this.scale*parentdiv.style.width+(this.startDate.getTime()))));;
    this.bars = [];
    this.barids = {};

    this.div = document.getElementById(newDiv(divid));
    this.header = document.getElementById(newDiv(this.div.id));
    this.graph = document.getElementById(newDiv(this.div.id));
    this.div.className = "ganttbg";
    this.div.style.width = ((this.endDate - this.startDate) / this.scale) + "px";
    this.header.style.height = this.headerHeight + "px";
    
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
    for(var i=barNb; i<this.bars.length; i++) 
        this.bars[i].draw();
}
OIGantt.prototype.addBar = function(id, dates, afterid, bgClass) {
    var newBar = new GanttBar(this, dates, bgClass || 0);
    var pos = this.bars.indexOf(this.barids[afterid]) + 1;
    this.bars.splice(pos, 0, newBar);
    this.barids[id] = newBar;
}
OIGantt.prototype.addFromTask = function(task, afterid, bgClass) {
    this.addBar(task.pk, [parseDate(task.fields.created),parseDate(task.fields.start_date),parseDate(task.fields.due_date)], afterid, bgClass);
}
OIGantt.prototype.addSpace = function(afterid) {
    var pos = this.bars.indexOf(this.barids[afterid]) + 1;
    if(this.bars[pos].dates.length) {
        this.bars.splice(pos, 0, new GanttBar(this, [], this.barids[afterid].bgClass));
        this.redraw();
    }
}
OIGantt.prototype.hideLine = function(id, nbnext) {
    var bar = this.barids[id];
    var pos = this.bars.indexOf(bar);
    this.div.removeChild(bar.bardiv);
    this.div.removeChild(bar.bgdiv);
    bar.bardiv = null;
    bar.bgdiv = null;
    this.bars.splice(pos, 1 + nbnext);
}
OIGantt.prototype.showLine = function(id, afterid) {
    var pos = this.bars.indexOf(this.barids[afterid]) + 1;
    this.bars.splice(pos, 0, this.barids[id]);
}
OIGantt.prototype.highlight = function(id) {
    this.barids[id].bardiv.className = "gantthighlight";
}
OIGantt.prototype.unhighlight = function(id) {
    this.barids[id].bardiv.className = "";
}
