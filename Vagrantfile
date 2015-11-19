# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

$provision = <<SCRIPT
echo I am provisioning...
sudo date > /etc/vagrant_provisioned_at
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q python-software-properties
sudo add-apt-repository ppa:presslabs/gitfs
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -q python-virtualenv python-dev libffi-dev build-essential libgit2-dev git-core
sudo adduser vagrant fuse
sudo sh -c "echo 'user_allow_other' >> /etc/fuse.conf"
virtualenv -q --setuptools /home/vagrant/gitfs
echo "source /home/vagrant/gitfs/bin/activate" >> /home/vagrant/.bashrc
echo Installing cffi
/home/vagrant/gitfs/bin/pip install -q 'cffi'
echo Installing requirements
/home/vagrant/gitfs/bin/pip install -q -r /vagrant/test_requirements.txt
echo Configuring git
git config --global user.email "vagrant@localhost"
git config --global user.name "Vagrant"
echo Installing gitfs
/home/vagrant/gitfs/bin/pip install -q -e /vagrant
echo "export TEST_DIR=/tmp/gitfs-tests" >> /home/vagrant/.bashrc
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty32"
  config.ssh.forward_agent = true
  config.vm.provision "shell", inline: $provision, privileged: false
end
