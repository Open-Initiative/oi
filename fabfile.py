from fabric.api import local, run, cd

def test():
    local("./manage.py test")

def init_south():
    run("oi/manage.py syncdb")
    run("oi/manage.py migrate messages --fake")
    run("oi/manage.py migrate projects --fake")
    run("oi/manage.py migrate users --fake")
    run("oi/manage.py migrate notification --fake")

def deploy_pp():
    local("git push pp")
    with cd("oi"):
        run("git merge devel")
        
def deploy_PROD():
    local("git push prod")
    with cd("oi"):
        run("git merge master")

def maintenance_PROD():
    run("mv www www.off;mv wwwtmp www")
    
def unmaintenance_PROD():
    run("mv www wwwtmp;mv www.off www")

def update():
    with cd("oi"):
        run("python update.py")
