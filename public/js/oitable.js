function OITable(divid, columns) {
    this.div = document.getElementById(divid);
    this.table = document.createElement("table");
    this.header = document.createElement("tr");
    this.lineheight = 30;
    this.space = null;
    
    var i;
    for(var column=columns[i=0]; i<columns.length; column=columns[++i]) {
        var th = document.createElement("th");
        th.className = "tableheader";
        th.title = ""+column;
        th.innerHTML = column;
        this.header.appendChild(th);
    }
    this.div.appendChild(this.table);
    this.init();
}
OITable.prototype.addSpace = function addSpace(afterid) {
    if(this.space && this.lines.indexOf(this.space) > -1) this.lines.splice(this.lines.indexOf(this.space), 1);
    this.space = this.addLine(0, [""], afterid, " "+this.lineids[afterid].className);
    this.redraw();
}
OITable.prototype.hideLine = function hideLine(id, nbnext) {
    var line = this.lineids[id];
    var pos = this.lines.indexOf(line);
    if(pos >= 0) this.lines.splice(pos, 1 + (nbnext||0));
}
OITable.prototype.showLine = function showLine(id, afterid) {
    if(this.lines.indexOf(this.lineids[id]) >= 0) this.lines.splice(this.lines.indexOf(this.lineids[id]), 1);
    var pos = this.lines.indexOf(this.lineids[afterid]) + 1;
    this.lines.splice(pos, 0, this.lineids[id]);
}
OITable.prototype.addLine = function addLine(id, cells, afterid, bgClass) {
    var line = document.createElement("tr");
    var i;
    for(var cell=cells[i=0]; i<cells.length; cell=cells[++i]) {
        col = document.createElement("td");
        col.title = ""+cell;
        col.innerHTML = cell;
        line.appendChild(col);
    }
    if(!id) line.firstChild.colSpan = this.header.getElementsByTagName('th').length;
    line.className = "tablebg" + (bgClass || 0);
    line.style.height = (this.lineheight-2) + "px";
    line.style.padding = "0";
    this.lineids[id] = line;
    var pos = this.lines.indexOf(this.lineids[afterid]) + 1;
    this.lines.splice(pos, 0, line);
    return line;
}
OITable.prototype.redraw = function redraw() {
    this.div.removeChild(this.table);
    this.table = document.createElement("table");
    this.table.className = "tablecell";
    this.div.appendChild(this.table);
    this.table.appendChild(this.header);
    for(var i=0; i < this.lines.length; i++)
        if(this.lines[i]) this.table.appendChild(this.lines[i]);
}
OITable.prototype.highlight = function highlight(id) {
    this.lineids[id].style.fontWeight = "bold";
}
OITable.prototype.unhighlight = function unhighlight(id) {
    this.lineids[id].style.fontWeight = "";
}
OITable.prototype.selectLine = function selectLine (id){
    this.lineids[id].className = " selected"+coloration;
    this.lineids[id].appendChild(document.createElement('div')).className = "selected-arrow";
}
OITable.prototype.init = function init (){
    this.lines = [];
    this.lineids = {};
    this.space = null;
}
