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

    $ git clone git@github.com:morninj/quickspin.git

Configuration
-------------

Copy `settings-sample.py` to `settings.py` and edit the variables in that 
file. For instance, to install nginx, set `nginx = True`. You should **read 
the whole file** and make sure the settings are correct.

### WordPress

If you want to install WordPress, edit `config/wp-config-sample.php` to 
include your database details and save it as `config/wp-config.php`. Make sure 
these details match the values for the MySQL database in `settings.py`.

### Config files

The files in the `config/` directory will replace the default config files on 
the server. The files are fine as-is, but they're there if you need to edit 
them.

Use
---

Make sure your settings in `settings.py` are correct, and then run:

    $ fab deploy

Some notes:

* If you're creating a new user, you'll need to enter a password for that 
  user. The other fields (`Full Name`, etc.) are optional.
* The firewall configuration may ask you: `Command may disrupt existing ssh 
  connections. Proceed with operation (y|n)?` Type `y` and press enter.

If you're installing MySQL, you will need to set a root password, which you 
will need later on. It will also ask several questions. Enter these responses:

    Change the root password? [Y/n] n
    Remove anonymous users? [Y/n] y
    Disallow root login remotely? [Y/n] y
    Remove test database and access to it? [Y/n] y
    Reload privilege tables now? [Y/n] y

When it's finished, the script will reboot the system to make sure all changes 
take effect.

To make sure the deployment was successful, connect to the server with your 
private key:

    $ ssh -i ~/path/to/your/key/id_dsa username@host.com

If you chose to install WordPress, you can configure your WordPress 
installation at `http://yoursite.com/`.

Feedback
--------

Send an email to [joseph] at [mornin] dot [org]. If others might be 
interested, you can [open an issue](https://github.com/morninj/quickspin/issues).
