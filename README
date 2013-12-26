Quickspin
=========

This tool automates web server deployment. It can install and configure a 
server, a database, WordPress, and basic security tools. It's best for small 
projects with low overhead.

I've only tested this configuration on Ubuntu Server 12.04.3 LTS 64-bit, but 
it should work on other Linux distributions with a little tweaking.

I like the small instances from [Digital 
Ocean](https://www.digitalocean.com/), but you can use any machine that allows 
root access, like Linode or Amazon EC2.

Installation
------------

Install [Fabric](http://docs.fabfile.org/en/1.8/):

    $ pip install fabric

Clone this repository:

    $ git clone ... TODO

Configuration
-------------

Copy `settings-sample.py` to `settings.py` and edit the variables in that 
file. For instance, to install nginx, make sure to set `nginx = True`.

### WordPress

If you want to install WordPress, edit `config/wp-config-sample.php` to 
include your database details and save it as `config/wp-config.php`. You will 
need the database details again when configuring MySQL.

### Config files

The files in the `config/` directory will replace the default config files on 
the server. The files are fine as-is, but they're there if you need to edit 
them.

`www.conf` (replaces `/etc/php5/fpm/pool.d/www.conf`):

* Change `listen = 127.0.0.1:9000` to `listen = /var/run/php5-fpm.sock`

`fastcgi_params` (replaces `/etc/nginx/fastcgi_params`):

* Change `SCRIPT_FILENAME` and add `PATH_INFO` (see 
  http://wiki.nginx.org/PHPFcgiExample)

`wp-sample-config.php`: as mentioned above, you'll need to edit the database 
values if you want to use WordPress.

`my.cnf`: TODO

Use
---

    $ fab deploy

Some notes:

* If you're creating a new user, you'll need to enter a password for that 
  user. The other fields (`Full Name`, etc.) are optional.
* The firewall configuration may ask you: `Command may disrupt existing ssh 
  connections. Proceed with operation (y|n)?` Type `y` and press enter.
* If you're installing MySQL, you'll need to enter a password several 
  times for the root user. This is a small hassle, but it lets you avoid 
  putting the root password in a file, which is a security risk.
* TODO: mysql questions



To make sure the deployment was successful, connect to the server with your 
private key:

    $ ssh -i ~/path/to/your/key/id_dsa username@host.com

