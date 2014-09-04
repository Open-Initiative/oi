#~ **install packages**
sudo apt-get install git apache2 mysql-server python-django python-mysqldb python-flup python-xapian python-docutils libapache2-mod-fcgid libapache2-mod-xsendfile python-setuptools fabric python-django-south python-pip
sudo pip install django-haystack xapian-haystack django-notification reportlab html2pdf html5lib PyGitHub django-cors-headers django-registration django_compressor lxml "BeautifulSoup<4.0" versiontools
sudo a2enmod rewrite
sudo a2enmod fcgid
sudo a2enmod xsendfile

#~ **system setup**
mkdir ../log
chmod +x oi/platforms/*/public/django.fcgi
chmod 744 manage.py

## **platform links creation**
#root
ln -sf /usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ oi/platforms/root/public/
ln -sf oi/platforms/root/public ../www_root
#funding
ln -sf /usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ oi/platforms/funding/public/
ln -sf oi/platforms/funding/public ../www_funding
#project
ln -sf /usr/lib/python2.7/dist-packages/django/contrib/admin/static/admin/ oi/platforms/project/public/
ln -sf oi/platforms/project/public ../www_project

#~ **Create database**
#mysql -u root -p -e "CREATE DATABASE OI; CREATE USER \"maxi\"; SET password FOR \"maxi\" = password(\"maximaxi1234\"); GRANT ALL ON OI.* TO \"maxi\""

import getpass

user = raw_input("Create a user for your database : ");
mdp = getpass.getpass('Create a password for you : ');
checkmdp = getpass.getpass("Check if the password is the same : ");
try = 0

while mdp != checkmdp:
    checkmdp = getpass.getpass("Sorry, please put the good password : ");
    try++;
    if try == 3:
        break;
    
if mdp == checkmdp:
    mysql -u root -p -e "CREATE DATABASE OI; CREATE USER "\".user."\"; SET password FOR "\".user."\" = password("\".mdp."\"); GRANT ALL ON OI.* TO "\".user."\""

#~ **Create all the notices in database**
./manage.py register_notices_types

#~ **Cconfigure Apache if the user wants**
read -p "Do you want us to configure apache automatically? [Yn]:" answer
case $answer in
    n|N|no|No) echo "Please configure your virtual directories to point to the files django.fcgi in the folders www_*";;
    *) ./apache2-conf.sh;;
esac
