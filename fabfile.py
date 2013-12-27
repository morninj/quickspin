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

def deploy():
    print 'Connecting to host %s...' % env.hosts[0]
    sudo('apt-get update && apt-get upgrade -y')
    if settings.add_new_user: add_new_user()
    if settings.security_tools: install_security_tools()
    create_web_directories()
    if settings.mysql: install_mysql()
    if settings.swap: configure_swap()
    if settings.nginx: install_nginx()
    if settings.php: install_php()
    if settings.wordpress: install_wordpress()
    print 'Configuration complete. Rebooting...'
    reboot()

def add_new_user():
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

def install_security_tools():
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

def create_web_directories():
    sudo('mkdir -p ' + webroot + '/htdocs/')
    sudo('mkdir -p ' + webroot + '/config')
    sudo('mkdir -p ' + webroot + '/logs/')
    sudo('chown -R www-data:www-data ' + webroot + '/htdocs/')
    sudo('chmod 755 ' + webroot)

def install_mysql():
    sudo('apt-get install -y mysql-server php5-mysql')
    sudo('mysql_install_db')
    sudo('/usr/bin/mysql_secure_installation')
    if settings.create_new_database:
        sudo('mysql -uroot -e "CREATE DATABASE ' + settings.database_name + '; CREATE USER ' + settings.database_user + '@localhost; SET PASSWORD FOR ' + settings.database_user + '@localhost= PASSWORD(\'' + settings.database_password + '\'); GRANT ALL PRIVILEGES ON ' + settings.database_name + '.* TO ' + settings.database_user + '@localhost IDENTIFIED BY \'' + settings.database_password + '\'; FLUSH PRIVILEGES;" -p')

def configure_swap():
    sudo('dd if=/dev/zero of=/swapfile bs=1024 count=' + settings.swap_size)
    sudo('mkswap /swapfile')
    sudo('swapon /swapfile')
    sudo('swapon -s')

def install_nginx():
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

def install_php():
    sudo('apt-get install -y php5-fpm')
    put('config/www.conf', '/etc/php5/fpm/pool.d/www.conf', use_sudo=True)
    put('config/fastcgi_params', '/etc/nginx/fastcgi_params', use_sudo=True)
    sudo('service php5-fpm restart')

def install_wordpress():
    sudo('wget -P ' + webroot + ' http://wordpress.org/latest.tar.gz')
    sudo('tar -xzvf ' + webroot + '/latest.tar.gz -C ' + webroot)
    sudo('mv ' + webroot  + '/wordpress/* ' + webroot + '/htdocs')
    sudo('rm ' + webroot + '/latest.tar.gz')
    sudo('rmdir ' + webroot + '/wordpress')
    put('config/wp-config.php', webroot + '/wp-config.php', use_sudo=True)
