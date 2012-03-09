function OITreeNode(id, tree, parent, color, bgClass) {
    this.id = id;
    this.tree = tree;
    this.parent = parent;
    this.color = color || 1;
    this.children = [];
    this.open = true;
    
    if(parent) this.div = document.getElementById(newDiv(this.parent.childDiv.id));
    else this.div = document.getElementById(newDiv(this.tree.div.id));
    this.div.className = "treebg"+bgClass%2;
    this.setContent(color);
    this.resetBtn(); //No idea why it is necessary to put this in a different method
}
OITreeNode.prototype.setContent = function setContent() {
    if(this.parent) {
        this.btn = document.createElement("img");
        this.btn.src = "/img/icons/treebtn"+this.color+"-closed.png";
        this.btn.id = "treebtn_"+this.id;
        this.btn.style.cssFloat = "left";
        this.btn.style.styleFloat = "left";
        this.btn.style.margin = "5px 0";
        this.div.appendChild(this.btn);
    }
    this.titleDiv = document.getElementById(newDiv(this.div.id));
    this.titleDiv.className = "treeelt state" + this.color;
    this.titleDiv.node = this;
    this.titleDiv.onmouseover = function() {if(oiTable) oiTable.highlight(this.node.id)};
    this.titleDiv.onmouseout = function() {if(oiTable) oiTable.unhighlight(this.node.id)};
    this.childDiv = document.getElementById(newDiv(this.div.id));
    this.childDiv.className = "treelist";
}
OITreeNode.prototype.resetBtn = function resetBtn() {
    if(this.parent) {
        this.btn = document.getElementById(this.btn.id);
        this.btn.node = this;
        this.btn.onclick = function(){this.node.expand();};
    }
}
OITreeNode.prototype.expand = function expand() {
    if(this.parent) {
        this.btn.src = "/img/icons/treebtn"+this.color+"-open.png";
        this.btn.onclick = function(){this.node.shrink();};
    }
    this.childDiv.style.display = "block";
    this.open = true;
    if(onExpandNode) onExpandNode(this.id);
}
OITreeNode.prototype.shrink = function shrink() {
    if(this.parent) {
        this.btn.src = "/img/icons/tree"+(this.parent?"btn":"root")+this.color+"-closed.png";
        this.btn.onclick = function(){this.node.expand();};
    }
    this.childDiv.style.display = "none";
    this.open = false;
    if(onShrinkNode) onShrinkNode(this.id);
}

function OITree(divid, expandCallback, shrinkCallback) {
    this.div = document.getElementById(divid);
    this.nodes = {};
    this.selected = null;
    this.expandCallback = expandCallback;
    this.shrinkCallback = shrinkCallback;
}
OITree.prototype.setRoot = function setRoot(rootid, color, bgClass) {
    this.root = new OITreeNode(rootid, this, null, color, bgClass);
    this.nodes[rootid] = this.root;
    return this.root.titleDiv;
}
OITree.prototype.addChild = function addChild(parentid, childid, color, bgClass) {
    var parentNode = this.nodes[parentid];
    var node = new OITreeNode(childid, this, parentNode, color, bgClass);
    parentNode.children.push(node);
    this.nodes[childid] = node;
    return node.titleDiv;
}
