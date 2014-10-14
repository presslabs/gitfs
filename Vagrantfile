# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

$provision = <<SCRIPT
echo I am provisioning...
date > /etc/vagrant_provisioned_at
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y -q python-software-properties
add-apt-repository ppa:presslabs/gitfs
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y -q python-virtualenv python-dev libffi-dev build-essential libgit2-dev git-core
adduser vagrant fuse
echo 'user_allow_other' >> /etc/fuse.conf
sudo -u vagrant virtualenv -q --setuptools /home/vagrant/gitfs
echo "source /home/vagrant/gitfs/bin/activate" >> /home/vagrant/.bashrc
sudo -u vagrant -- /home/vagrant/gitfs/bin/pip install -q fusepy
sudo -u vagrant -- /home/vagrant/gitfs/bin/pip install -q -e /vagrant
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "hashicorp/precise32"
  config.ssh.forward_agent = true
  config.vm.provision "shell", inline: $provision
end
