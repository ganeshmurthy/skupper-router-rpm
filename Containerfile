#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

# Gets the latest Fedora from dockerhub
FROM fedora:38

MAINTAINER "dev@pid.apache.org"

RUN dnf -y install gcc gcc-c++ cmake libuuid-devel openssl openssl-devel cyrus-sasl-devel cyrus-sasl-plain cyrus-sasl-gssapi swig git make python3-qpid-proton qpid-proton-c-devel systemd rpmdevtools rpmlint valgrind emacs libwebsockets-devel python3-devel curl libnghttp2-devel nmap-ncat asciidoc rpkg tox libffi-devel python3-setuptools libunwind-devel fedpkg
WORKDIR /
RUN rpmdev-setuptree
COPY ./skupper-router-2.4.3.tar.gz /root/rpmbuild/SOURCES
COPY ./qpid-proton-0.39.0.tar.gz /root/rpmbuild/SOURCES
COPY ./licenses.xml /root/rpmbuild/SOURCES
COPY ./PROTON-2764-2763-2748.patch /root/rpmbuild/SOURCES
COPY ./skupper-router.spec /root/rpmbuild/SPECS
COPY ./CMakeLists.txt.patch /root/rpmbuild/SOURCES
RUN rpmbuild -bb /root/rpmbuild/SPECS/skupper-router.spec && rpm -U ~/rpmbuild/RPMS/noarch/skupper-router-common-2.4.3-1.fc38.noarch.rpm && rpm -U ~/rpmbuild/RPMS/x86_64/skupper-router-2.4.3-1.fc38.x86_64.rpm && rpm -U ~/rpmbuild/RPMS/noarch/skupper-router-tools-2.4.3-1.fc38.noarch.rpm

CMD ["skrouterd"]
#CMD ["/bin/bash"]


