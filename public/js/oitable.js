function OITable(divid, columns) {
    this.div = document.getElementById(divid);
    this.table = document.createElement("table");
    this.header = document.createElement("tr");
    this.lineheight = 20;
    this.space = null;
    
    var i;
    for(var column=columns[i=0]; i<columns.length; column=columns[++i]) {
        th = document.createElement("th");
        th.className = "tableheader";
        th.innerHTML = column;
        this.header.appendChild(th);
    }
    this.div.appendChild(this.table);
    this.lines = [];
    this.lineids = {};
}
OITable.prototype.addSpace = function(afterid) {
    if(this.space) this.lines.splice(this.lines.indexOf(this.space), 1);
    this.space = this.addLine(0, [""], afterid, " "+this.lineids[afterid].className);
    this.redraw();
}
OITable.prototype.hideLine = function(id, nbnext) {
    line = this.lineids[id];
    pos = this.lines.indexOf(line);
    this.lines.splice(pos, 1 + nbnext);
}
OITable.prototype.showLine = function(id, afterid) {
    pos = this.lines.indexOf(this.lineids[afterid]) + 1;
    this.lines.splice(pos, 0, this.lineids[id]);
}
OITable.prototype.addLine = function(id, cells, afterid, bgClass) {
    var line = document.createElement("tr");
    var i;
    for(var cell=cells[i=0]; i<cells.length; cell=cells[++i]) {
        col = document.createElement("td");
        col.innerHTML = cell;
        line.appendChild(col);
    }
    if(!id) line.firstChild.colSpan = "10";
    line.className = "tablebg" + (bgClass || 0);
    line.style.height = (this.lineheight-2) + "px";
    line.style.padding = "0";
    this.lineids[id] = line;
    pos = this.lines.indexOf(this.lineids[afterid]) + 1;
    this.lines.splice(pos, 0, line);
    return line;
}
OITable.prototype.addFromTask = function(task, afterid, bgClass) {
    if(this.div.id == "budget") this.addLine(task.pk, [(parseFloat(task.fields.offer) || parseFloat(task.fields.alloffer_sum)) + " €", (parseFloat(task.fields.bid_sum) || parseFloat(task.fields.allbid_sum)) + " €"], afterid, bgClass);
    if(this.div.id == "team") this.addLine(task.pk, [task.fields.assignee_get_profile_get_display_name, task.fields.bid_set_count], afterid, bgClass);
}
OITable.prototype.redraw = function() {
    this.div.removeChild(this.table);
    this.table = document.createElement("table");
    this.div.appendChild(this.table);
    this.table.appendChild(this.header);
    for(var i=0; i < this.lines.length; i++)
        if(this.lines[i]) this.table.appendChild(this.lines[i]);
}
OITable.prototype.highlight = function(id) {
    this.lineids[id].style.fontWeight = "bold";
}
OITable.prototype.unhighlight = function(id) {
    this.lineids[id].style.fontWeight = "";
}
