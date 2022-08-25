ostree --repo=./rhcos-os-content-arm/srv/repo show e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27

alias osr='ostree --repo=/data/iefcu/rhcos-os-content-arm/srv/repo'
ostree --repo=./rhcos-os-content-arm/srv/repo show e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27
osr show e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27


osr commit --branch=e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27 rhcos-rootfs-arm

osr diff e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27 ./rhcos-rootfs-arm

# 修改rhcos-rootfs-arm目录中的vmlinuz文件，然后再commit
osr commit --branch=e3f59f25256a43b961899ab086d51c58168e888101de610e72884f21c3d90a27 ./rhcos-rootfs-arm
