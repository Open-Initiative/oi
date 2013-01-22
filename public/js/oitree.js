function OITreeNode(id, tree, parent, color, has_children) {
    this.id = id;
    this.tree = tree;
    this.parent = parent;
    this.color = color || 1;
    this.children = [];
    this.open = true;
    
    if(parent) this.div = document.getElementById(newDiv(this.parent.childDiv.id));
    else this.div = document.getElementById(newDiv(this.tree.div.id));
    this.div.node = this;
    this.setContent(has_children);
    this.resetBtn(); //No idea why it is necessary to put this in a different method
    if('onmouseenter' in this.div) //test browser support for onmouseenter
        this.div.onmouseenter = this.over;
    else
        this.div.onmouseover = function(evt){
            target=evt.relatedTarget;
            while(target){if(this===target)return;target=target.parentNode;}
            this.node.over.call(this, evt);
        };
    this.titleDiv.onmousedown = this.drag;
    this.titleDiv.receiveNode = function receiveNode(id) {
            if(id!=this.node.id) onMoveNode(id,this.node.id);
        };
}
OITree.prototype.deleteNode = function(projectid){
    var node = this.nodes[projectid];
    if(node){
        node.parent.children.pop(node);
        node.div.parentNode.removeChild(node.div);
        OITreeNode[projectid] = null;
    }
}
OITreeNode.prototype.setContent = function setContent(has_children) {
    if(this.parent) {
        if(has_children){
            this.btn = document.createElement("img");
            this.btn.src = "/img/icons/treebtn"+this.color+"-closed.png";
            this.btn.id = "treebtn_"+this.id;
            this.btn.style.cssFloat = "left";
            this.btn.style.styleFloat = "left";
            this.btn.style.margin = "5px 0";
            this.div.appendChild(this.btn);
          } 
        
        if(this.color < 2 && !has_children){
            /*create del button for all the tasks*/
            this.del = document.createElement("img");
            this.del.src = "/img/icons/delete.png";
            this.del.alt= "delete task";
            this.del.title= "delete task";
            this.del.className = "clickable";
            this.del.style.cssFloat = "right";
            this.del.style.marginTop = "10px";
            this.del.style.display = "none";
            this.del.node = this;
            this.projectid = this.id;
            this.del.onclick = function(){
                if(oiTree.deleteCallback){oiTree.deleteCallback(this.node.id);};
            };
            this.div.appendChild(this.del);
            
            /*create edit button for all the tasks*/
            this.edit = document.createElement("img");
            this.edit.src = "/img/icons/edit.png";
            this.edit.alt = "edit title";
            this.edit.title = "edit title";
            this.edit.className = "clickable";
            this.edit.style.cssFloat = "right";
            this.edit.style.marginRight = "5px";
            this.edit.style.marginLeft = "5px";
            this.edit.style.marginTop = "10px";
            this.edit.style.display = "none";
            this.edit.node = this;
            this.edit.onclick = function(){
                var newtitle = prompt(gettext("Please insert a title :"), "");
                if(newtitle){
                    if(oiTree.editCallback) oiTree.editCallback(this.node.id, newtitle);
                }
            };
            this.div.appendChild(this.edit);          
        }
    }
    this.titleDiv = document.getElementById(newDiv(this.div.id));
    this.titleDiv.className = "treeelt state" + this.color;
    this.titleDiv.node = this;
    
    this.titleDiv.onmouseover = function() {
        if(oiTable) oiTable.highlight(this.node.id);
        if(this.node.del && this.node.edit){
            this.node.del.style.display = "inline";
            this.node.edit.style.display = "inline";
        }
    };
    
    this.titleDiv.onmouseout = function() {
        if(oiTable) oiTable.unhighlight(this.node.id);
        if(this.node.del && this.node.edit){
            this.node.del.style.display = "none";
            this.node.edit.style.display = "none";
        }
    };
    
    this.childDiv = document.getElementById(newDiv(this.div.id));
    this.childDiv.className = "treelist";
}
OITreeNode.prototype.setColor = function setColor() {
    this.div.className = "treebg" + (this.parent?this.parent.children.indexOf(this):0)%2;
}
OITreeNode.prototype.over = function over() {
    if(window.draggedNode && this.lastChild.className!="treenext") {
        var next = document.createElement("div");
        next.className = "treenext";
        next.receiveNode = function receiveNode(id){
            var node = this.parentNode.node;
            if(id!=node.id) onMoveNode(id,node.parent.id, node.id);
        };
        this.appendChild(next);
        if('onmouseleave' in this) //test browser support for onmouseleave
            this.onmouseleave = function() {this.removeChild(this.lastChild);this.onmouseleave = null;};
        else 
            this.onmouseout = function(evt){
                target=evt.relatedTarget;
                while(target){if(this===target)return;target=target.parentNode;}
                this.removeChild(this.lastChild);this.onmouseout = null;
                return false;
            };
    }
}
OITreeNode.prototype.drag = function drag() {
    window.draggedNode=this.node;
    document.onmouseup=window.draggedNode.drop;
    window.draggedDiv=this.node.titleDiv.cloneNode(true);
    window.draggedDiv.style.position="absolute";
    document.body.appendChild(window.draggedDiv);
    document.onmousemove= function(evt){
        var event = evt||window.event;
        window.draggedDiv.style.top=(event.clientY+document.documentElement.scrollTop+3)+"px";
        window.draggedDiv.style.left=(event.clientX+document.documentElement.scrollLeft+3)+"px";
    }
    document.body.style.cursor = "pointer";
    return false;
}
OITreeNode.prototype.drop = function drop(evt) {
    var target = (evt||window.event).target;
    while(target && !target.receiveNode) target = target.parentNode;
    if(target) target.receiveNode(window.draggedNode.id, evt||window.event);
    window.draggedNode = null;
    document.body.removeChild(window.draggedDiv);
    window.draggedDiv = null;
    document.onmouseup = null;
    document.onmousemove = null;
    document.body.style.cursor = "default";
    return false;
}
OITreeNode.prototype.addChild = function addChild(childid, color, afterid, has_children) {
    var node = this.tree.nodes[childid];
    if(node) {
        node.parent.children.splice(node.parent.children.indexOf(node), 1);
        node.parent.childDiv.removeChild(node.div);
        if(this.children.length) {
            node.parent = this;
            if(afterid) this.childDiv.insertBefore(node.div, this.tree.nodes[afterid].div.nextSibling);
            else this.childDiv.appendChild(node.div);
            this.children.push(node);
        } else this.tree.nodes[childid] = null;
    } else {
        node = new OITreeNode(childid, this.tree, this, color, has_children);
        this.tree.nodes[childid] = node;
        this.children.push(node);
    }
    node.setColor();
    return node.titleDiv;
}
OITreeNode.prototype.resetBtn = function resetBtn() {
    if(this.parent && this.btn) {
        this.btn = document.getElementById(this.btn.id);
        this.btn.node = this;
        this.btn.onclick = function(){this.node.expand();};
    }
}
OITreeNode.prototype.expand = function expand() {
    if(this.parent && this.btn) {
        this.btn.src = "/img/icons/treebtn"+this.color+"-open.png";
        this.btn.onclick = function(){this.node.shrink();};
    }
    this.childDiv.style.display = "block";
    this.open = true;
    if(this.tree.expandCallback) this.tree.expandCallback(this.id);
}
OITreeNode.prototype.shrink = function shrink() {
    if(this.parent && this.btn) {
        this.btn.src = "/img/icons/tree"+(this.parent?"btn":"root")+this.color+"-closed.png";
        this.btn.onclick = function(){this.node.expand();};
    }
    this.childDiv.style.display = "none";
    this.open = false;
    if(this.tree.shrinkCallback) this.tree.shrinkCallback(this.id);
}
OITreeNode.prototype.getLastChild = function getLastChild() {
    if(this.children.length) return this.children[this.children.length-1].id;
    else return this.id;
}

function OITree(divid, expandCallback, shrinkCallback, deleteCallback, editCallback) {
    this.div = document.getElementById(divid);
    this.init();
    this.expandCallback = expandCallback;
    this.shrinkCallback = shrinkCallback;
    this.deleteCallback = deleteCallback;
    this.editCallback = editCallback;
}
OITree.prototype.init = function init() {
    this.div.innerHTML = "";
    this.nodes = {};
    this.selected = null;
    this.root = null;
}
OITree.prototype.setRoot = function setRoot(rootid, color, bgClass) {
    this.root = new OITreeNode(rootid, this, null, color, bgClass);
    this.nodes[rootid] = this.root;
    return this.root.titleDiv;
}
