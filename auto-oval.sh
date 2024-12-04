#!/bin/bash
METAXML=com.ubuntu.$(lsb_release -cs).usn.oval.xml
METAXML=oci.com.ubuntu.$(lsb_release -cs).pkg.oval.xml
METAXML=com.ubuntu.$(lsb_release -cs).usn.oval.xml

CVE
com.ubuntu.noble.cve.oval.xml.bz2
com.ubuntu.realtime_noble.cve.oval.xml.bz2
oci.com.ubuntu.noble.cve.oval.xml.bz2
oci.com.ubuntu.realtime_noble.cve.oval.xml.bz2

PKG
com.ubuntu.noble.pkg.oval.xml.bz2
com.ubuntu.realtime_noble.pkg.oval.xml.bz2
oci.com.ubuntu.noble.pkg.oval.xml.bz2
oci.com.ubuntu.realtime_noble.pkg.oval.xml.bz2

USN
com.ubuntu.noble.usn.oval.xml.bz2
oci.com.ubuntu.noble.usn.oval.xml.bz2

https://chatgpt.com/share/67500a1c-2d48-8013-97eb-5146254bfb36
 	
wget https://security-metadata.canonical.com/oval/$METAXML.bz2
bunzip2 $METAXML.bz2
oscap oval eval --report report.html $METAXML

#Cloud Ubuntu 20.04
#wget https://security-metadata.canonical.com/oval/oci.com.ubuntu.focal.usn.oval.xml.bz2
#bunzip2 oci.com.ubuntu.focal.usn.oval.xml.bz2
#wget -O manifest https://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64-root.manifest
#oscap oval eval --report report.html oci.com.ubuntu.focal.usn.oval.xml

xdg-open report.html 2>/dev/null
rm $METAXML
