# second change
# refer /boot/loader/grub-conf.sh

# 挂载磁盘, 注意修改磁盘路径sda
sudo mount /dev/sda4 /mnt # 根分区
sudo mount /dev/sda3 /mnt/boot # boot分区

echo "Configuration start..."

sudo cp /boot/ostree/rhcos-bca69e93a4fe930a67b6a03b121690776fc0fb42f0545504bdfe0a0451fb9ca5/initrd-kb26-inside.img /mnt/boot/ostree/rhcos-bca69e93a4fe930a67b6a03b121690776fc0fb42f0545504bdfe0a0451fb9ca5/initrd-inside.img
sudo cp /boot/ostree/rhcos-bca69e93a4fe930a67b6a03b121690776fc0fb42f0545504bdfe0a0451fb9ca5/initrd-kb26-inside.img /mnt/boot/ostree/rhcos-03dea0747b6365fb2c2b09ebbec6f7905e9d2ffeeb09f4abb37ba69374446285/initrd-inside.img

sudo cp /boot/ostree/rhcos-bca69e93a4fe930a67b6a03b121690776fc0fb42f0545504bdfe0a0451fb9ca5/vmlinuz-4.19.90-2003.4.0.0036.ky3.kb26.aarch64  /mnt/boot/ostree/rhcos-bca69e93a4fe930a67b6a03b121690776fc0fb42f0545504bdfe0a0451fb9ca5/vmlinuz-4.19.90
sudo cp /boot/ostree/rhcos-bca69e93a4fe930a67b6a03b121690776fc0fb42f0545504bdfe0a0451fb9ca5/vmlinuz-4.19.90-2003.4.0.0036.ky3.kb26.aarch64  /mnt/boot/ostree/rhcos-03dea0747b6365fb2c2b09ebbec6f7905e9d2ffeeb09f4abb37ba69374446285/vmlinuz-4.19.90

# TODO: modify
sudo cp -ar /lib/modules/4.19.90-2003.4.0.0036.ky3.kb26.aarch64 /mnt/ostree/deploy/rhcos/deploy/e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27.0/lib/modules/
# TOOD: modify
sudo cp -ar /lib/modules/4.19.90-2003.4.0.0036.ky3.kb26.aarch64 /mnt/ostree/deploy/rhcos/deploy/e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27.1/lib/modules/

sync

sudo cp /mnt/boot/loader/entries/ostree-1-rhcos.conf /mnt/boot/loader/entries/ostree-1-rhcos.conf.bak
sudo cp /mnt/boot/loader/entries/ostree-2-rhcos.conf /mnt/boot/loader/entries/ostree-2-rhcos.conf.bak

sudo sed -i "s/Red Hat Enterprise Linux CoreOS/KylinSec Linux CloudOS/g" /mnt/boot/loader/entries/ostree-1-rhcos.conf
sudo sed -i "s/vmlinuz-4.18.0-305.19.1.el8_4.aarch64/vmlinuz-4.19.90/g" /mnt/boot/loader/entries/ostree-1-rhcos.conf
sudo sed -i "s/initramfs-4.18.0-305.19.1.el8_4.aarch64.img/initrd-inside.img/g" /mnt/boot/loader/entries/ostree-1-rhcos.conf

sudo sed -i "s/Red Hat Enterprise Linux CoreOS/KylinSec Linux CloudOS/g" /mnt/boot/loader/entries/ostree-2-rhcos.conf
sudo sed -i "s/vmlinuz-4.18.0-305.19.1.el8_4.aarch64/vmlinuz-4.19.90/g" /mnt/boot/loader/entries/ostree-2-rhcos.conf
sudo sed -i "s/initramfs-4.18.0-305.19.1.el8_4.aarch64.img/initrd-inside.img/g" /mnt/boot/loader/entries/ostree-2-rhcos.conf

sync

echo "Done!"
