sudo apt-get install -y software-properties-common python-software-properties
sudo add-apt-repository -y ppa:presslabs/testing-ppa
sudo apt-get update
sudo apt-get install -y udev fuse-utils libfuse-dev libfuse2 libgit2-0 libgit2-dev git git-core

sudo mknod /dev/fuse -m 0666 c 10 229
sudo chown root:root /dev/fuse
adduser travis group
sudo chmod g+rw /dev/fuse
exec su -l $USER
