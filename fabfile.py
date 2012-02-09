from fabric.api import local, run, cd

def test():
    local("./manage.py test")

def init_south():
    run("./manage.py syncdb")
    run("./manage.py migrate messages --fake")
    run("./manage.py migrate projects --fake")
    run("./manage.py migrate users --fake")
    run("./manage.py migrate notification --fake")

def deploy_pp():
    local("git push pp")
    with cd("oi"):
        run("git merge devel")
