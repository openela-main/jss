################################################################################
Name:           jss
################################################################################

%global         product_id idm-jss

# Upstream version number:
%global         major_version 4
%global         minor_version 11
%global         update_version 0

Summary:        Java Security Services (JSS)
URL:            https://github.com/dogtagpki/jss
License:        MPLv1.1 or GPLv2+ or LGPLv2+

# For development (i.e. unsupported) releases, use x.y.z-0.n.<phase>.
# For official (i.e. supported) releases, use x.y.z-r where r >=1.
%global         release_number 1
Version:        %{major_version}.%{minor_version}.%{update_version}
Release:        %{release_number}%{?_timestamp}%{?_commit_id}%{?dist}
#global         _phase -alpha1

# To generate the source tarball:
# $ git clone https://github.com/dogtagpki/jss.git
# $ cd jss
# $ git tag v4.5.<z>
# $ git push origin v4.5.<z>
# Then go to https://github.com/dogtagpki/jss/releases and download the source
# tarball.
Source:         https://github.com/dogtagpki/jss/archive/v%{version}%{?_phase}/jss-%{version}%{?_phase}.tar.gz

# md2man not available on i686
ExcludeArch: i686


# To create a patch for all changes since a version tag:
# $ git format-patch \
#     --stdout \
#     <version tag> \
#     > jss-VERSION-RELEASE.patch
# Patch: jss-VERSION-RELEASE.patch

################################################################################
# Java
################################################################################

%if 0%{?fedora} && 0%{?fedora} <= 32 || 0%{?rhel} && 0%{?rhel} <= 8
%define java_devel java-1.8.0-openjdk-devel
%define java_headless java-1.8.0-openjdk-headless
%define java_home /usr/lib/jvm/jre-1.8.0-openjdk
%else
%define java_devel java-11-openjdk-devel
%define java_headless java-11-openjdk-headless
%define java_home /usr/lib/jvm/jre-11-openjdk
%endif

################################################################################
# Build Options
################################################################################

# By default the build will execute unit tests unless --without tests
# option is specified.

%bcond_without tests

################################################################################
# Build Dependencies
################################################################################

BuildRequires:  make
BuildRequires:  cmake >= 3.14
BuildRequires:  zip
BuildRequires:  unzip

BuildRequires:  gcc-c++
BuildRequires:  nss-devel >= 3.44
BuildRequires:  nss-tools >= 3.44
BuildRequires:  %{java_devel}
BuildRequires:  jpackage-utils
BuildRequires:  slf4j
BuildRequires:  glassfish-jaxb-api
BuildRequires:  slf4j-jdk14
BuildRequires:  apache-commons-lang3

BuildRequires:  junit

%description
Java Security Services (JSS) is a java native interface which provides a bridge
for java-based applications to use native Network Security Services (NSS).
This only works with gcj. Other JREs require that JCE providers be signed.

################################################################################
%package -n %{product_id}
################################################################################

Summary:        Java Security Services (JSS)

Requires:       nss >= 3.44
Requires:       %{java_headless}
Requires:       jpackage-utils
Requires:       slf4j
Requires:       glassfish-jaxb-api
Requires:       slf4j-jdk14
Requires:       apache-commons-lang3

Obsoletes:      jss < %{version}-%{release}
Provides:       jss = %{version}-%{release}
Provides:       jss = %{major_version}.%{minor_version}
Provides:       %{product_id} = %{major_version}.%{minor_version}

Conflicts:      ldapjdk < 4.20
Conflicts:      idm-console-framework < 1.2
Conflicts:      tomcatjss < 7.6.0
Conflicts:      pki-base < 10.10.0

%description -n %{product_id}
Java Security Services (JSS) is a java native interface which provides a bridge
for java-based applications to use native Network Security Services (NSS).
This only works with gcj. Other JREs require that JCE providers be signed.

################################################################################
%package -n %{product_id}-javadoc
################################################################################

Summary:        Java Security Services (JSS) Javadocs

Obsoletes:      jss-javadoc < %{version}-%{release}
Provides:       jss-javadoc = %{version}-%{release}
Provides:       jss-javadoc = %{major_version}.%{minor_version}
Provides:       %{product_id}-javadoc = %{major_version}.%{minor_version}

%description -n %{product_id}-javadoc
This package contains the API documentation for JSS.

################################################################################
%prep
################################################################################

%autosetup -n jss-%{version}%{?_phase} -p 1

################################################################################
%build
################################################################################

%set_build_flags

# Enable compiler optimizations
export BUILD_OPT=1

# Generate symbolic info for debuggers
CFLAGS="-g $RPM_OPT_FLAGS"
export CFLAGS

# Check if we're in FIPS mode
modutil -dbdir /etc/pki/nssdb -chkfips true | grep -q enabled && export FIPS_ENABLED=1

# The Makefile is not thread-safe
%cmake \
    -DVERSION=%{version} \
    -DJAVA_HOME=%{java_home} \
    -DJAVA_LIB_INSTALL_DIR=%{_jnidir} \
    -DJSS_LIB_INSTALL_DIR=%{_libdir}/jss \
    -B %{_vpath_builddir}

cd %{_vpath_builddir}

%{__make} \
    VERBOSE=%{?_verbose} \
    CMAKE_NO_VERBOSE=1 \
    --no-print-directory \
    all

%{__make} \
    VERBOSE=%{?_verbose} \
    CMAKE_NO_VERBOSE=1 \
    --no-print-directory \
    javadoc

%if %{with tests}
ctest --output-on-failure
%endif

################################################################################
%install
################################################################################

cd %{_vpath_builddir}

%{__make} \
    VERBOSE=%{?_verbose} \
    CMAKE_NO_VERBOSE=1 \
    DESTDIR=%{buildroot} \
    INSTALL="install -p" \
    --no-print-directory \
    install

################################################################################
%files -n %{product_id}
################################################################################

%defattr(-,root,root,-)
%doc jss.html
%license MPL-1.1.txt gpl.txt lgpl.txt
%{_libdir}/*
%{_jnidir}/*

################################################################################
%files -n %{product_id}-javadoc
################################################################################

%defattr(-,root,root,-)
%{_javadocdir}/jss-%{version}/

################################################################################
%changelog
* Thu Feb 08 2024 Red Hat PKI Team <rhcs-maint@redhat.com> 4.11.0-1
- Rebase to JSS 4.11.0

* Tue Jan 16 2024 Red Hat PKI Team <rhcs-maint@redhat.com> 4.10.0-0.1
- Rebase to JSS 4.10.0-alpha1

* Fri Jan 12 2024 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.8-1
- Rebase to JSS 4.9.8

* Wed Jun 01 2022 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.4-1
- Rebase to JSS 4.9.4
- Bug 2013674 - JSS cannot be properly initialized after using another NSS-backed security provider

* Tue Feb 15 2022 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.3-1
- Rebase to JSS 4.9.3
- Bug 2046022 - CVE-2021-4213 pki-core:10.6/jss: memory leak in TLS connection leads to OOM [rhel-8]

* Mon Nov 15 2021 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.2-1
- Rebase to JSS 4.9.2

* Tue Sep 21 2021 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.1-1
- Rebase to JSS 4.9.1

* Mon Jul 26 2021 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.0-1
- Rebase to JSS 4.9.0

* Fri Jun 11 2021 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.0-0.2
- Rebase to JSS 4.9.0-alpha2

* Wed Jun 02 2021 Red Hat PKI Team <rhcs-maint@redhat.com> 4.9.0-0.1
- Rebase to JSS 4.9.0-alpha1

* Thu Jan 14 2021 Red Hat PKI Team <rhcs-maint@redhat.com> 4.8.1-1
- Rebase to upstream JSS v4.8.1
- Red Hat Bugilla #1908541 - jss broke SCEP - missing PasswordChallenge class
- Red Hat Bugilla #1489256 - [RFE] jss should support RSA with OAEP padding

* Wed Nov 18 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.8.0-2
- Only check PKCS11Constants on beta builds
- Bump tomcatjss, pki-core conflicts due to lang3

* Wed Oct 28 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.8.0-1
- Rebase to upstream JSS v4.8.0

* Tue Oct 20 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.8.0-0.1
- Rebase to upstream JSS v4.8.0-b1

* Fri Sep 11 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.7.3-1
- Rebase to upstream stable release JSS v4.7.3
- Red Hat Bugzilla #1873235 - Fix SSL_ERROR_INAPPROPRIATE_FALLBACK_ALERT in pki ca-user-cert-add

* Thu Aug 06 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.7.2-1
- Rebase to upstream stable release JSS v4.7.2
- Red Hat Bugzilla #1822246 - Fix SSLSocket NULL pointer deference after close

* Fri Jul 31 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.7.1-1
- Rebase to upstream stable release JSS v4.7.1

* Thu Jul 09 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.7.0-1
- Rebase to upstream stable release JSS v4.7.0
- Fixed TestSSLEngine

* Thu Jun 25 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.7.0-0.4
- Rebased to JSS 4.7.0-b4

* Mon Jun 22 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.7.0-0.3
- Rebased to JSS 4.7.0-b3

* Tue May 26 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.7.0-0.1
- Rebased to JSS 4.7.0-b1

* Mon Mar 23 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.2-4
- Red Hat Bugzilla #1807371 - KRA-HSM: Async and sync key recovery using kra agent web is failing

* Mon Mar 02 2020 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.2-3
- Red Hat Bugzilla #1807371 - KRA-HSM: Async and sync key recovery using kra agent web is failing

* Tue Oct 29 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.2-2
- Red Hat Bugzilla #1730767 - JSS: Wrap NSS CMAC + KDF implementations
- Rebased to JSS 4.6.2

* Wed Sep 11 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-5
- Red Hat Bugzilla #1747987 - CVE 2019-14823 jss: OCSP policy "Leaf and Chain" implicitly trusts the root certificate

* Wed Aug 14 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-4
- Red Hat Bugzilla #1698059 - pki-core implements crypto

* Tue Jul 16 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-3
- Red Hat Bugzilla #1721135 - JSS - LD_FLAGS support

* Wed Jun 12 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-2
- Minor updates to release

* Wed Jun 12 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.6.0-1
- Rebased to JSS 4.6.0

* Thu Apr 25 2019 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.3-1
- Rebased to JSS 4.5.3

* Fri Aug 10 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-1
- Rebased to JSS 4.5.0

* Tue Aug 07 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.6
- Rebased to JSS 4.5.0-b1

* Tue Aug 07 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.5
- Red Hat Bugzilla #1612063 - Do not override system crypto policy (support TLS 1.3)

* Fri Jul 20 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.4
- Rebased to JSS 4.5.0-a4
- Red Hat Bugzilla #1604462 - jss: FTBFS in Fedora rawhide

* Thu Jul 05 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.3
- Rebased to JSS 4.5.0-a3

* Fri Jun 22 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.2
- Rebased to JSS 4.5.0-a2

* Fri Jun 15 2018 Red Hat PKI Team <rhcs-maint@redhat.com> 4.5.0-0.1
- Rebased to JSS 4.5.0-a1
