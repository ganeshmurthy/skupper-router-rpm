# skupper-router-rpm

Run the following commands to create an upstream rpm for skupper-router

1. podman build -t gmurthy/fedora38/skupper-router-rpm --file=Containerfile .
2. podman run --net host -it gmurthy/fedora38/skupper-rpm
3. The skupper-router rpms are available ~/rpmbuild/RPMS folder and is installed in the container

4. The container already runs the following two commands
  rpm -U ~/rpmbuild/RPMS/noarch/skupper-router-common-2.4.3-1.fc38.noarch.rpm
  rpm -U ~/rpmbuild/RPMS/x86_64/skupper-router-2.4.3-1.fc38.x86_64.rpm
5. When you run the Containerfile as shown in Step #2, skrouterd will be launched

