#!/bin/bash
echo "error: this script isn't fully tested, and is just documentation"
exit 1

sudo yum update -y
sudo yum install -y httpd php8.2 mariadb105 php-mysql

# start up apache
sudo systemctl start httpd
sudo systemctl enable httpd

# Create MySQL database and user for WordPress
sudo mysql -u root -p"your_mysql_root_password" <<MYSQL_SCRIPT
CREATE DATABASE wordpress;
CREATE USER 'wordpress' IDENTIFIED BY 'wordpress-pass';
GRANT ALL PRIVILEGES ON wordpress.* TO wordpress;
FLUSH PRIVILEGES;
EXIT;
MYSQL_SCRIPT



########
# XXX/TODO
exit 0

wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
cd wordpress
cp wp-config-sample.php wp-config.php

###########


# Download and configure WordPress
wget https://wordpress.org/latest.tar.gz
tar -zxvf latest.tar.gz
sudo mv wordpress/* /var/www/html/
sudo chown -R apache:apache /var/www/html/
sudo chmod -R 755 /var/www/html/
sudo cp /var/www/html/wp-config-sample.php /var/www/html/wp-config.php
sudo sed -i 's/database_name_here/wordpress/g' /var/www/html/wp-config.php
sudo sed -i 's/username_here/wordpressuser/g' /var/www/html/wp-config.php
sudo sed -i 's/password_here/yourpassword/g' /var/www/html/wp-config.php

# Restart Apache
sudo systemctl restart httpd

