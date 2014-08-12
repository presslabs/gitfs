sudo apt-get install -y software-properties-common python-software-properties
sudo add-apt-repository -y ppa:presslabs/testing-ppa
sudo apt-get update
sudo apt-get install -y udev fuse-utils libfuse-dev libfuse2 libgit2-0 libgit2-dev git git-core

sudo mknod /dev/fuse -m 0777 c 10 229
sudo chown travis:travis /dev/fuse
sudo adduser travis fuse
