function OITreeNode(id, tree, parent, color) {
    this.id = id;
    this.tree = tree;
    this.parent = parent;
    this.color = color || 1;
    this.children = [];
    this.open = true;
    
    if(parent) this.div = document.getElementById(newDiv(this.parent.childDiv.id));
    else this.div = document.getElementById(newDiv(this.tree.div.id));
    this.setContent(color);
    this.resetBtn(); //No idea why it is necessary to put this in a different method
    this.titleDiv.onmousedown = function(){
            window.draggedNode=this.node;
            document.onmouseup=window.draggedNode.drop;
            document.body.style.cursor = "pointer";
            return false;
        };
    this.titleDiv.receiveNode = function receiveNode(id) {
            if(id!=this.node.id)
                if(onMoveNode && onMoveNode(id, this.node.id))
                    this.node.addChild(id);
        }
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
OITreeNode.prototype.setColor = function setColor() {
    this.div.className = "treebg" + (this.parent?this.parent.children.indexOf(this):0)%2;
}
OITreeNode.prototype.drop = function drop(evt) {
    var target = evt.originalTarget || evt.target;
    while(target && !target.receiveNode) target = target.parentNode;
    if(target) target.receiveNode(window.draggedNode.id, evt);
    window.draggedNode = null;
    document.onmouseup = null;
    document.body.style.cursor = "default";
}
OITreeNode.prototype.addChild = function addChild(childid, color) {
    var node = this.tree.nodes[childid];
    if(node) {
        node.parent.children.splice(node.parent.children.indexOf(node), 1);
        node.parent.childDiv.removeChild(node.div);
        if(this.children.length) {
            node.parent = this;
            this.childDiv.appendChild(node.div);
            this.children.push(node);
        } else this.tree.nodes[childid] = null;
    } else {
        node = new OITreeNode(childid, this.tree, this, color);
        this.tree.nodes[childid] = node;
        this.children.push(node);
    }
    node.setColor();
    return node.titleDiv;
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
OITreeNode.prototype.getLastChild = function getLastChild() {
    if(this.children.length) return this.children[this.children.length-1].id;
    else return this.id;
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
