# skupper-router-rpm

Run the following commands to create an upstream rpm for skupper-router

1. podman build -t gmurthy/fedora38/skupper-router-rpm --file=Containerfile-skupper-rpm .
2. podman run --net host -it gmurthy/fedora38/skupper-rpm
3. The skupper-router rpms are installed in the ~/rpmbuild/RPMS folder

4. First install the skupper-router-common rpm
  rpm -U ~/rpmbuild/RPMS/noarch/skupper-router-common-2.4.3-1.fc38.noarch.rpm
5. Now, install the skupper-router rpm
  rpm -U ~/rpmbuild/RPMS/x86_64/skupper-router-2.4.3-1.fc38.x86_64.rpm
