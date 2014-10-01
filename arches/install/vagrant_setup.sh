cd /vagrant/arches/install
chmod u+x ./ubuntu_precise_setup.sh
./ubuntu_precise_setup.sh

cd /vagrant/arches/es/elasticsearch-1.1.1/bin
chmod u+x ./elasticsearch.in.sh
./elasticsearch.in.sh
chmod u+x elasticsearch
./elasticsearch

cd /vagrant/arches/install
chmod u+x ./install_dependencies.sh
./install_dependencies.sh

cd /vagrant/arches/build
chmod u+x ./install_arches_db.sh
chmod u+x ./install_packages.sh
./install_arches_db.sh
./install_packages.sh
