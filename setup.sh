#~ **install packages**
sudo apt-get install git apache2 mysql-server python-django python-mysqldb python-flup python-xapian python-docutils libapache2-mod-fcgid libapache2-mod-xsendfile python-setuptools python-reportlab fabric python-django-south python-pip
sudo easy_install django-haystack xapian-haystack django-notification pisa html5lib PyGitHub django-cors-headers django-registration django_compressor lxml "BeautifulSoup<4.0" versiontools 
#sudo pip install django-email-bandit
sudo a2enmod rewrite
sudo a2enmod fcgid

#~ **clone oi repository**
git clone ssh://pp.open-initiative@ssh.alwaysdata.com/home/pp.open-initiative/oi

#~ **system setup**
mkdir log
chmod +x oi/public/django*.fcgi
chmod 744 oi/manage.py
ln -s /usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ oi/public/
#that was before, now it's admin
#mv oi/public/admin oi/public/media
ln -s oi/public ./
mv ./public ./www

#~ **Create database**
mysql -u root -p -e "CREATE DATABASE OI; CREATE USER \"maxi\"; SET password FOR \"maxi\" = password(\"maximaxi1234\"); GRANT ALL ON OI.* TO \"maxi\""
oi/manage.py syncdb
oi/manage.py migrate


