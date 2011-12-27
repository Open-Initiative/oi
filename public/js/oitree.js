function OITreeNode(id, tree, parent, color, bgClass) {
    this.id = id;
    this.tree = tree;
    this.parent = parent;
    this.color = color || 1;
    this.children = [];
    this.selected = false;
    this.open = true;
    
    if(parent) this.div = document.getElementById(newDiv(this.parent.childDiv.id));
    else this.div = document.getElementById(newDiv(this.tree.div.id));
    this.div.className = "treebg"+bgClass%2;
    this.setContent(color);
    this.resetBtn(); //No idea why it is necessary to put this in a different method
}
OITreeNode.prototype.setContent = function() {
    this.btn = document.createElement("img");
    this.btn.src = "/img/icons/treebtn"+this.color+"-closed.png";
    this.btn.id = "treebtn_"+this.id;
    this.btn.style.cssFloat = "left";
    this.div.appendChild(this.btn);
    this.titleDiv = document.getElementById(newDiv(this.div.id));
    this.titleDiv.className = "treeelt" + this.color;
    this.titleDiv.node = this;
    this.titleDiv.onmouseover = function() {if(this.node.tree.gantt) this.node.tree.gantt.highlight(this.node.id)};
    this.titleDiv.onmouseout = function() {if(this.node.tree.gantt) this.node.tree.gantt.unhighlight(this.node.id)};
    this.childDiv = document.getElementById(newDiv(this.div.id));
    this.childDiv.className = "treelist";
}
OITreeNode.prototype.resetBtn = function() {
    this.btn = document.getElementById(this.btn.id);
    this.btn.node = this;
    this.btn.onclick = function(){this.node.expand();};
}
OITreeNode.prototype.expand = function() {
    this.btn.src = "/img/icons/treebtn"+this.color+"-open.png";
    this.btn.onclick = function(){this.node.shrink();};
    this.childDiv.style.display = "block";
    this.open = true;
    if(onExpandNode) onExpandNode(this.id);
}
OITreeNode.prototype.shrink = function() {
    this.btn.src = "/img/icons/treebtn"+this.color+"-closed.png";
    this.btn.onclick = function(){this.node.expand();};
    this.childDiv.style.display = "none";
    this.open = false;
    if(onShrinkNode) onShrinkNode(this.id);
}

function OITree(divid, expandCallback, shrinkCallback) {
    this.div = document.getElementById(divid);
    this.nodes = {};
    this.expandCallback = expandCallback;
    this.shrinkCallback = shrinkCallback;
}
OITree.prototype.setRoot = function(rootid, color, bgClass) {
    this.root = new OITreeNode(rootid, this, null, color, bgClass);
    this.nodes[rootid] = this.root;
    return this.root.titleDiv;
}
OITree.prototype.addChild = function(parentid, childid, color, bgClass) {
    parent = this.nodes[parentid];
    node = new OITreeNode(childid, this, parent, color, bgClass);
    parent.children.push(node);
    this.nodes[childid] = node;
    return node.titleDiv;
}
