#~ **install packages**
sudo apt-get install git apache2 mysql-server python-django python-mysqldb python-flup python-xapian python-docutils libapache2-mod-fcgid libapache2-mod-xsendfile python-setuptools python-reportlab fabric python-django-south python-pip
sudo easy_install django-haystack xapian-haystack django-notification pisa html5lib PyGitHub django-cors-headers django-registration django_compressor lxml "BeautifulSoup<4.0" versiontools 
#sudo pip install django-email-bandit
sudo a2enmod rewrite
sudo a2enmod fcgid
sudo a2enmod xsendfile

#~ **clone oi repository**
#git clone ssh://pp.open-initiative@ssh.alwaysdata.com/home/pp.open-initiative/oi

#~ **system setup**
mkdir ../log
chmod +x oi/platforms/*/public/django.fcgi
chmod 744 manage.py
#that was before, now it's admin
#mv oi/public/admin oi/public/media
#root
ln -s /usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ oi/platforms/root/public/
ln -s oi/platforms/root/public ../www_root
#funding
ln -s /usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ oi/platforms/funding/public/
ln -s oi/platforms/funding/public ../www_funding
#project
ln -s /usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ oi/platforms/project/public/
ln -s oi/platforms/project/public ../www_project

#~ **Create database**
mysql -u root -p -e "CREATE DATABASE OI; CREATE USER \"maxi\"; SET password FOR \"maxi\" = password(\"maximaxi1234\"); GRANT ALL ON OI.* TO \"maxi\""
./manage.py syncdb
./manage.py migrate

#~ **Create all the notices in database**
./manage.py register_notices_types

#~ **Cconfigure Apache if the user wants**
read -p "Do you want us to configure apache automatically? [Yn]:" answer
case $answer in
    n|N|no|No) echo "Please configure your virtual directories to point to the files django.fcgi in the folders www_*";;
    *) ./apache2-conf.sh;;
esac
