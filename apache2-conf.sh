#!/bin/bash

sudo cat <<EOF > /etc/apache2/sites-available/000-default.conf
<VirtualHost *:8050>

	ServerAdmin webmaster@localhost
	DocumentRoot $PWD/www
	<Directory $PWD/www>
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
sudo cat <<EOF > /etc/apache2/sites-available/001-funding.conf
<VirtualHost *:8051>

	ServerAdmin webmaster@localhost
	DocumentRoot $PWD/www
	<Directory $PWD/www>
		Options FollowSymLinks MultiViews ExecCGI
		AllowOverride None
		Order allow,deny
		Allow from all
		RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ django_funding.fcgi/$1 [QSA,L]
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
EOF
sudo cat <<EOF > /etc/apache2/sites-available/002-project.conf
<VirtualHost *:8052>

	ServerAdmin webmaster@localhost
	DocumentRoot $PWD/www
	<Directory $PWD/www>
		Options FollowSymLinks MultiViews ExecCGI
		AllowOverride None
		Order allow,deny
		Allow from all
		RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^(.*)$ django_projects.fcgi/$1 [QSA,L]
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

</VirtualHost>

# vim: syntax=apache ts=4 sw=4 sts=4 sr noet
EOF

sudo ln -s /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-enabled/000-default.conf
sudo ln -s /etc/apache2/sites-available/001-funding.conf /etc/apache2/sites-enabled/001-funding.conf
sudo ln -s /etc/apache2/sites-available/002-project.conf /etc/apache2/sites-enabled/002-project.conf

#~ **configuration for port.conf

#Listen *:80
#Listen *:8050
#Listen *:8051
#Listen *:8052

#NameVirtualHost *:80
#NameVirtualHost *:8050
#NameVirtualHost *:8051
#NameVirtualHost *:8052

