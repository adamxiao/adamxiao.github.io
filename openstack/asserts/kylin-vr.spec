Name:       kylin-vr
Version:    0.1
Release:    1
Summary:    Kylin Virtual Router package
License:    FIXME

Source0:    kylin-vr-0.1.tar.gz

#Requires:   python3-pip NetworkManager
Requires:   NetworkManager iptables python-netifaces PyYAML

%description
Kylin Virtual Router package

%prep
%setup -q

%build

%post

systemctl daemon-reload >/dev/null 2>&1
systemctl enable kylin-vr >/dev/null 2>&1

cat > /etc/udev/rules.d/80-kylin-vr.rules << EOF
ACTION=="add", SUBSYSTEM=="net", RUN+="/usr/bin/kylin-vr.py -c reload"
ACTION=="del", SUBSYSTEM=="net", RUN+="/usr/bin/kylin-vr.py -c reload"
EOF

sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config
sed -i 's/^BLACKLIST_RPC/#&/' /etc/sysconfig/qemu-ga

cat > /etc/sysctl.d/kylin-vr.conf << EOF
net.ipv4.ip_forward = 1
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
EOF

# NetworkManager conf
cat > /etc/NetworkManager/conf.d/kylin-vr.conf << EOF
[main]
no-auto-default=*
EOF

%postun

rm -rf /etc/udev/rules.d/80-kylin-vr.rules
rm -rf /etc/sysctl.d/kylin-vr.conf

%install
mkdir -p %{buildroot}/etc/kylin-vr
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/lib/systemd/system
install -m 755 kylin-vr.py %{buildroot}/usr/bin/kylin-vr.py
install -m 644 kylin-vr.yaml %{buildroot}/etc/kylin-vr/kylin-vr.yaml
install -m 644 kylin-vr.service %{buildroot}/lib/systemd/system/kylin-vr.service


%files
/usr/bin/kylin-vr.py
/etc/kylin-vr/kylin-vr.yaml
/lib/systemd/system/kylin-vr.service

%changelog
# let's skip this for now
