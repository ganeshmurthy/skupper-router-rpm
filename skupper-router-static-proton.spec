# Define pkgdocdir for releases that don't define it already
%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%global _use_systemd 1

%global proton_minimum_version 0.37.0
%global libwebsockets_minimum_version 4.3.1
%global libnghttp2_minimum_version 1.33.0

%global proton_vendored_version 0.39.0
%global embedded_proton_version qpid-proton-%{proton_vendored_version}
%define proton_install_prefix %{_builddir}/%{embedded_proton_version}/install

%global buildnum 1

%undefine __brp_mangle_shebangs

Name:          skupper-router
Version:       2.4.3
Release:       %{buildnum}%{?dist}
Summary:       Skupper router
License:       ASL 2.0
URL:           http://skupper.io/
#Source0:       http://www.github.com/skupperproject/skupper-router/archive/refs/tags/%{version}.tar.gz
Source0:       skupper-router-%{version}.tar.gz
Source2:       licenses.xml
# proton
Source5:       %{embedded_proton_version}.tar.gz
# This patch contains fixes to three proton issues - 
# c542df80 PROTON-2764: schedule failed raw connections from pn_listener_raw_accept() so they can process events and cleanup
# 0987726b PROTON-2763: Raw connection double DISCONNECT event
# cb637b79 PROTON-2748: Raw connection async close fix and tests. First part of pull 402
Source6:       PROTON-2764-2763-2748.patch
Source7:       CMakeLists.txt.patch

%define red_hat_version %{version}-%{buildnum}

%global _pkglicensedir %{_licensedir}/%{name}-%{version}
%{!?_licensedir:%global license %doc}
%{!?_licensedir:%global _pkglicensedir %{_pkgdocdir}}

ExcludeArch: i686


#Patch3:        dispatch.patch

# proton deps (not building bindings so don't need python, ruby)
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  pkgconfig
BuildRequires:  libuuid-devel
BuildRequires:  openssl-devel
BuildRequires:  cyrus-sasl-devel

# router deps
#BuildRequires: qpid-proton-c-devel >= %{proton_minimum_version}
BuildRequires: python3-qpid-proton >= %{proton_minimum_version}
# This is required for proton 0.38.0 and above
BuildRequires: cmake
BuildRequires: openssl-devel
BuildRequires: libwebsockets-devel >= %{libwebsockets_minimum_version}
BuildRequires: libnghttp2-devel >= %{libnghttp2_minimum_version}

%if 0%{?fedora} || (0%{?rhel} && 0%{?rhel} >= 7)
BuildRequires: asciidoc >= 8.6.8
BuildRequires: systemd
%endif


#%package 
#Summary:  The Skupper Router executable
Requires:  python3
Requires: skupper-router-common == %{version}

# proton
#Requires:  qpid-proton-c%{?_isa} >= %{proton_minimum_version}
Requires:  python3-qpid-proton >= %{proton_minimum_version}

%if %{_use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

Requires: libwebsockets >= %{libwebsockets_minimum_version}
Requires: libnghttp2 >= %{libnghttp2_minimum_version}

%description
A lightweight message router, written in C and built on Qpid Proton, that provides flexible and scalable interconnect backend for skupper.io Level 7 Virtual Application Networks


%files
%license %{_pkglicensedir}/LICENSE
%license %{_pkglicensedir}/licenses.xml
%{_sbindir}/skrouterd
%config(noreplace) %{_sysconfdir}/skupper-router/skrouterd.conf
%config(noreplace) %{_sysconfdir}/sasl2/skrouterd.conf
%{_exec_prefix}/lib/skupper-router
%{python3_sitelib}/skupper_router_site.py*
%{python3_sitelib}/skupper_router/
%{python3_sitelib}/skupper_router-*.egg-info
%{python3_sitelib}/__pycache__/*
/usr/share/skupper-router/html/index.html

%if %{_use_systemd}

%{_unitdir}/skrouterd.service

%endif

%{_mandir}/man5/skrouterd.conf.5*
%{_mandir}/man8/skrouterd.8*

%pre
getent group skrouterd >/dev/null || groupadd -r skrouterd
getent passwd skrouterd >/dev/null || \
  useradd -r -M -g skrouterd -d %{_localstatedir}/lib/skrouterd -s /sbin/nologin \
    -c "Owner of Skrouterd Daemons" skrouterd
exit 0


%if %{_use_systemd}

%post
/sbin/ldconfig
%systemd_post skrouterd.service

%preun
%systemd_preun skrouterd.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart skrouterd.service

%endif



%package docs
Summary:   Documentation for the Skupper router
BuildArch: noarch

%description docs
%{summary}.


%files docs
%doc %{_pkgdocdir}
%license %{_pkglicensedir}/LICENSE
%license %{_pkglicensedir}/licenses.xml

%package common
Summary:  Internal code shared between the router daemon and the tools
BuildArch: noarch
Requires: python3
Requires: python3-qpid-proton >= %{proton_minimum_version}

%description common
%{summary}.

%files common
%{_exec_prefix}/lib/skupper-router/python/skupper_router_internal/


%package tools
Summary: skstat and skmanage tools for skrouterd
BuildArch: noarch

# proton
Requires: python3-qpid-proton >= %{proton_minimum_version}
Requires: skupper-router-common == %{version}


%description tools
%{summary}.


%files tools
%{_bindir}/skstat
%{_bindir}/skmanage

%{_mandir}/man8/skstat.8*
%{_mandir}/man8/skmanage.8*


%prep
%setup -q
%setup -q -D -b 5 -n qpid-proton-%{proton_vendored_version}

#%patch3 -p1
#%patch4 -p1

# downstream only - patch the proton make
pushd %{_builddir}/%{embedded_proton_version}
patch -p1 < %{SOURCE6}
popd
pushd %{_builddir}/skupper-router-%{version}
patch -p1 < %{SOURCE7}
popd

%build

cd %{_builddir}/%{embedded_proton_version}

#%__cmake . -B "%{__cmake_builddir}"  \
%cmake . -B "%{__cmake_builddir}"  \
    -DCMAKE_C_FLAGS="$CMAKE_CXX_FLAGS $CFLAGS -Wno-error=deprecated-declarations" \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_TESTING=OFF \
    -DBUILD_BINDINGS=OFF \
    -DBUILD_TLS=ON -DSSL_IMPL=openssl \
    -DBUILD_STATIC_LIBS=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=%{proton_install_prefix} \
    -DLIB_INSTALL_DIR:PATH=%{proton_install_prefix}/usr/lib64 \
    -DINCLUDE_INSTALL_DIR:PATH=%{proton_install_prefix}/usr/include

cmake --build "%{__cmake_builddir}"
cmake --install "%{__cmake_builddir}"
#%__cmake --build "%{__cmake_builddir}" %{?_smp_mflags} --verbose
#%__cmake --install "%{__cmake_builddir}"

export DOCS=ON

cd %{_builddir}/skupper-router-%{version}

%cmake -DVERSION=%{red_hat_version} \
       -DDOC_INSTALL_DIR=%{?_pkgdocdir} \
       -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DUSE_SETUP_PY=0 \
       -DQD_DOC_INSTALL_DIR=%{_pkgdocdir} \
       "-DBUILD_DOCS=$DOCS" \
       -DCMAKE_SKIP_RPATH:BOOL=OFF \
       -DUSE_LIBWEBSOCKETS=ON \
       -DUSE_LIBNGHTTP2=ON \
       -DCONSOLE_INSTALL=OFF \
       -DPython_EXECUTABLE=%{python3} \
       -DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON \
       -DProton_USE_STATIC_LIBS=ON \
       -DProton_DIR=%{proton_install_prefix}/usr/lib64/cmake/Proton \
       "-DCMAKE_C_FLAGS=$CMAKE_CXX_FLAGS $CFLAGS -Wno-error=deprecated-declarations" \
       .


# to fix multilib install, force (any) known date to generated file (and patched .py files)
#touch -r %{SOURCE5} %{_builddir}/skupper-router-%{version}/tests/system_tests_edge_router.py
#touch -r %{SOURCE5} %{_builddir}/skupper-router-%{version}/tests/system_tests_one_router.py
#touch -r %{SOURCE5} %{_builddir}/skupper-router-%{version}/tests/system_tests_ssl.py

%cmake_build --target all --target man
#make doc
#make


%install
cd %{_builddir}/skupper-router-%{version}
%cmake_install

%if %{_use_systemd}

install -dm 755 %{buildroot}%{_unitdir}
install -pm 644 %{_builddir}/skupper-router-%{version}/etc/fedora/skrouterd.service \
                %{buildroot}%{_unitdir}

%endif

install -dm 755 %{buildroot}/var/run/skupper-router

install -dm 755 %{buildroot}%{_pkglicensedir}
install -pm 644 %{SOURCE2} %{buildroot}%{_pkglicensedir}
install -pm 644 %{buildroot}%{_pkgdocdir}/LICENSE %{buildroot}%{_pkglicensedir}
rm -f %{buildroot}%{_pkgdocdir}/LICENSE

rm -f  %{buildroot}/%{_includedir}/qpid/dispatch.h
rm -fr %{buildroot}/%{_includedir}/qpid/dispatch
rm -fr %{buildroot}/share/index.html

#%post -p /sbin/ldconfig

#%postun -p /sbin/ldconfig


%changelog
* Tue Sep 19 2023 Ganesh Murthy <gmurthy@redhat.com> - 2.4.3-1
- Rebase to 2.4.3 skupper-router

* Sun Jul 23 2023 Ganesh Murthy <gmurthy@redhat.com> - 2.4.2-1
- Rebase to 2.4.2 skupper-router

* Wed Jun 28 2023 Ganesh Murthy <gmurthy@redhat.com> - 2.4.1-2
- Bumped buildnum to 2

* Tue Jun 20 2023 Ganesh Murthy <gmurthy@redhat.com> - 2.4.1-1
- Rebase to 2.4.1 skupper-router

* Wed Jun 14 2023 Ganesh Murthy <gmurthy@redhat.com> - 2.4.0-1
- Rebase to 2.4.0 skupper-router

* Tue Feb 7 2023 Ganesh Murthy <gmurthy@redhat.com> - 2.3.0-1
- Rebase to 2.3.0 skupper-router

* Wed Jan 11 2023 Ganesh Murthy <gmurthy@redhat.com> - 2.2.1-1
- Rebase to 2.2.1 skupper-router

* Tue Dec 20 2022 Mike Cressman <mcressma@redhat.com> - 2.2.0-3
- Finalize the version string

* Fri Dec 16 2022 Mike Cressman <mcressma@redhat.com> - 2.2.0-2
- Update the version to include upstream and downstream info

* Mon Nov 14 2022 Ganesh Murthy <gmurthy@redhat.com> - 2.2.0-1
- Rebase to 2.2.0 skupper-router

* Fri Oct 14 2022 Ganesh Murthy <gmurthy@redhat.com> - 2.1.0-1
- Rebase to 2.1.0 skupper-router

* Fri Jun 3 2022 Mike Cressman <mcressma@redhat.com> - 2.0.2-1
- Rebase to 2.0.2 skupper-router

* Thu May 5 2022 Mike Cressman <mcressma@redhat.com> - 2.0.1-3
- Initial build of skupper-router for Application Interconnect 1.0
