# TODO line length
from fabric.api import *
from fabric.operations import put
import settings

env.hosts = [settings.server_address]
env.user = settings.root_username
if settings.root_use_password:
    env.password = settings.root_password
else:
    env.key_filename = settings.root_private_key
webroot = settings.web_directory + settings.site_name
nginx_conf = webroot + '/config/' + settings.site_name

# TODO separate functions

def deploy():
    print 'Connecting to host %s...' % env.hosts[0]
    run('uname')
    # Update package lists and upgrade existing packages
    sudo('apt-get update && apt-get upgrade -y')
    # Add new user
    sudo('adduser ' + settings.my_username)
    sudo('adduser %s sudo' % settings.my_username)
    # Upload user's private key
    put(settings.my_public_key, '/var/tmp/public_key')
    sudo('mkdir /home/%s/.ssh/' % settings.my_username)
    sudo('cat /var/tmp/public_key >> /home/%s/.ssh/authorized_keys' % \
        settings.my_username)
    sudo('rm /var/tmp/public_key')
    sudo('chmod 700 /home/%s/.ssh' % settings.my_username)
    sudo('chmod 400 /home/%s/.ssh/authorized_keys' % settings.my_username)
    sudo('chown {0}:{0} /home/{0} -R'.format(settings.my_username))
    # Install security tools:
        if security_tools:
        # Install fail2ban to block suspicious activity
        sudo('apt-get install -y fail2ban')
        # Only allow SSH key access
        sudo('echo "PasswordAuthentication no" >> /etc/ssh/sshd_config')
        # Prevent root login
        sudo('echo "PermitRootLogin no" >> /etc/ssh/sshd_config')
        # Configure firewall
        for port in settings.allowed_ports:
            sudo('ufw allow ' + port)
        sudo('ufw enable')
        # Enable automatic security updates
        if settings.enable_automatic_security_updates:
            sudo('apt-get install unattended-upgrades -y')
            sudo('echo \'APT::Periodic::Update-Package-Lists "1";\' > /etc/apt/apt.conf.d/10periodic')
            sudo('echo \'APT::Periodic::Download-Upgradeable-Packages "1";\' >> /etc/apt/apt.conf.d/10periodic')
            sudo('echo \'APT::Periodic::AutocleanInterval "7";\' >> /etc/apt/apt.conf.d/10periodic')
            sudo('echo \'APT::Periodic::Unattended-Upgrade "1";\' >> /etc/apt/apt.conf.d/10periodic')
    # Create web directories
    sudo('mkdir -p ' + webroot + '/htdocs/')
    sudo('mkdir -p ' + webroot + '/config')
    sudo('mkdir -p ' + webroot + '/logs/')
    sudo('chown -R www-data:www-data ' + webroot + '/htdocs/')
    sudo('chmod 755 ' + webroot)
    # Install MySQL
    if settings.mysql:
        sudo('apt-get install -y mysql-server php5-mysql')
        sudo('mysql_install_db')
        sudo('/usr/bin/mysql_secure_installation')
        if settings.create_new_database:
            sudo('mysql -uroot -e "CREATE DATABASE ' + settings.database_name + '" -p')
            sudo('mysql -uroot -e "CREATE USER ' + settings.database_user + '@localhost" -p')
            sudo('mysql -uroot -e "SET PASSWORD FOR ' + settings.database_user + '@localhost= PASSWORD(\'' + settings.database_password + '\')" -p')
            sudo('mysql -uroot -e "GRANT ALL PRIVILEGES ON ' + settings.database_name + '.* TO ' + settings.database_user + '@localhost IDENTIFIED BY \'' + settings.database_password + '\';" -p')
            sudo('mysql -uroot -e "FLUSH PRIVILEGES" -p')
            # TODO: only one mysql command
        # TODO my.cnf
    # Configure swap
    if settings.swap:
        sudo('dd if=/dev/zero of=/swapfile bs=1024 count=' + settings.swap_size)
        sudo('mkswap /swapfile')
        sudo('swapon /swapfile')
        sudo('swapon -s')
    # Install nginx
    if settings.nginx:
        sudo('apt-get install -y nginx')
        sudo('service nginx start')
        sudo('update-rc.d nginx defaults') # Start nginx on boot
        # Configure nginx virtual host
        sudo('echo "server {" > ' + nginx_conf)
        sudo('echo "    server_name ' + settings.site_name + ';" >> ' + nginx_conf) # TODO subdomains?
        sudo('echo "    root ' + webroot + '/htdocs;" >> ' + nginx_conf)
        sudo('echo "    index index.html index.php;" >> ' + nginx_conf)
        sudo('echo "    error_log ' + webroot + '/logs/error.log info;" >> ' + nginx_conf)
        sudo('echo "    access_log ' + webroot + '/logs/access.log;" >> ' + nginx_conf)
        if settings.wordpress:
            sudo('echo "    " >> ' + nginx_conf)
            sudo("echo '    location / { try_files $uri $uri/ /index.php?q=$uri&$args; }' >>" + nginx_conf)
            sudo('echo "    " >> ' + nginx_conf)
        if settings.php:
            # Add PHP conf to nginx conf
            sudo('echo "    " >> ' + nginx_conf)
            sudo('echo "    location ~ \.php$ {" >> ' + nginx_conf)
            sudo("echo '        try_files $uri =404;' >> " + nginx_conf)
            sudo('echo "        fastcgi_pass unix:/var/run/php5-fpm.sock;" >> ' + nginx_conf)
            sudo('echo "        fastcgi_index index.php;" >> ' + nginx_conf)
            sudo('echo "        include fastcgi_params;" >> ' + nginx_conf)
            sudo('echo "    }" >> ' + nginx_conf)
            sudo('echo "<?php phpinfo(); ?>" > ' + webroot + '/htdocs/test.php')
        sudo('echo "}" >> ' + nginx_conf)
        sudo('ln -s ' + nginx_conf + ' /etc/nginx/sites-enabled/' + settings.site_name)
        sudo('service nginx restart')
    # Install PHP
    if settings.php:
        sudo('apt-get install php5-fpm')
        put('config/www.conf', '/etc/php5/fpm/pool.d/www.conf', use_sudo=True)
        put('config/fastcgi_params', '/etc/nginx/fastcgi_params', use_sudo=True)
        sudo('service php5-fpm restart')
    # Install Wordpress
    if settings.wordpress:
        sudo('wget -P ' + webroot + ' http://wordpress.org/latest.tar.gz')
        sudo('tar -xzvf ' + webroot + '/latest.tar.gz -C ' + webroot)
        sudo('mv ' + webroot  + '/wordpress/* ' + webroot + '/htdocs')
        sudo('rm ' + webroot + '/latest.tar.gz')
        sudo('rmdir ' + webroot + '/wordpress')
        put('config/wp-config.php', webroot + '/wp-config.php', use_sudo=True)
    if settings.nginx:
        sudo('service nginx restart')
