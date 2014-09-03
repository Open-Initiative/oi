#!/bin/bash

cat <<EOF > 000-default.conf
<VirtualHost *:8050>

	ServerAdmin webmaster@localhost
	DocumentRoot $PWD/../www_root
	<Directory $PWD/../www_root>
		Options FollowSymLinks MultiViews ExecCGI
		AllowOverride None
		Order allow,deny
		Allow from all
		RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ django.fcgi/$1 [QSA,L]
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
EOF
cat <<EOF > 001-funding.conf
<VirtualHost *:8051>

	ServerAdmin webmaster@localhost
	DocumentRoot $PWD/../www_funding
	<Directory $PWD/../www_funding>
		Options FollowSymLinks MultiViews ExecCGI
		AllowOverride None
		Order allow,deny
		Allow from all
		XSendFile On
		XSendFilePath $PWD/OIFS
		RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ django.fcgi/$1 [QSA,L]
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
EOF
cat <<EOF > 002-project.conf
<VirtualHost *:8052>

	ServerAdmin webmaster@localhost
	DocumentRoot $PWD/../www_project
	<Directory $PWD/../www_project>
		Options FollowSymLinks MultiViews ExecCGI
		AllowOverride None
		Order allow,deny
		Allow from all
		XSendFile On
		XSendFilePath $PWD/OIFS
		RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ django.fcgi/$1 [QSA,L]
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
EOF

sudo mv 00*.conf /etc/apache2/sites-available/

sudo ln -sf /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-enabled/000-default.conf
sudo ln -sf /etc/apache2/sites-available/001-funding.conf /etc/apache2/sites-enabled/001-funding.conf
sudo ln -sf /etc/apache2/sites-available/002-project.conf /etc/apache2/sites-enabled/002-project.conf


echo "configuration for port.conf:"
echo "Listen *:80"
echo "Listen *:8050"
echo "Listen *:8051"
echo "Listen *:8052"
