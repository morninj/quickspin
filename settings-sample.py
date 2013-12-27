# Server address
server_address = '' # IP address (10.11.12.13) or domain name (example.com)

# Credentials for the server administrator
root_username = '' # E.g., ubuntu
root_use_password = False # False: use private key; True: use password
root_password = ''
root_private_key = '' # Local path to the root user's private key--e.g., ~/.aws/yourname.pem

# Credentials for the user who will be interacting with the server
# For security, this user will only be able to access the server using a SSH 
# key (see https://en.wikipedia.org/wiki/Secure_Shell#Key_management)
# This script will create the user on the server and upload your public key
add_new_user = True
my_username = ''
my_public_key = '' # Local path to your public key--e.g., ~/.ssh/id_dsa.pub

# Site name (your site's domain name)
site_name = '' # E.g., yoursite.com

# Web directory (where publicly accessible files live)
# Site files will live in web_directory/yoursite.com/htdocs/, ./logs/, etc.
web_directory = '/var/sites/'

# Install security tools?
security_tools = True

# Firewall configuration: allow traffic on these ports
allowed_ports = ['22', '80', '443']

# Enable automatic security updates?
enable_automatic_security_updates = True

# Tools
nginx = True
mysql = True
php = True
wordpress = True

# MySQL config
# Make sure these values match the values in config/wp-config.php
create_new_database = True
database_name = '' 
database_user = '' 
database_password = '' 

# Swap (recommended for MySQL on small servers)
swap = True
swap_size = '512k'
