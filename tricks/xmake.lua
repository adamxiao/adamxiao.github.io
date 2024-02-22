-- refer defs.mk
add_cflags("-g" ,"-Wall" ,"-fno-strict-aliasing" ,"-D_GNU_SOURCE" ,"-D_FILE_OFFSET_BITS=64" ,"-DPTHREAD_STACK_MIN=0" ,"-D_LARGEFILE_SOURCE")
add_cxflags("-g" ,"-Wall" ,"-fno-strict-aliasing" ,"-D_GNU_SOURCE" ,"-D_FILE_OFFSET_BITS=64" ,"-DPTHREAD_STACK_MIN=0" ,"-D_LARGEFILE_SOURCE")

-- refer defs.mk
add_defines("PRODBLD=\"adam-R101F20\"")
add_defines("VARPREFIX=\"/var/lib/ksvd\"")
add_defines("PRODLOGDIR=\"/var/log/ksvd\"")
add_defines("PRODRUNDIR=\"/var/run/ksvd\"")
add_defines("PRODPREFIX=\"/usr/lib/ksvd\"")
add_defines("PRODVERINT=7")
add_defines("PRODVER=\"7\"")
add_defines("BUILD_DATE=\"02/06/24 14:31\"") -- TODO: 根据当前时间生成

add_includedirs("lib/boost") -- 每一个makefile中都有，提上来
add_includedirs("common/include") -- refer rules.mk

target("uniqbpro_c")
    set_kind("static")
    add_files(
    "common/src/libuniqbpro/aes.cpp"
    ,"common/src/libuniqbpro/http_client.cpp"
    ,"common/src/libuniqbpro/tcp-relay.cpp"
    ,"common/src/libuniqbpro/timezone.cpp"
    ,"common/src/libuniqbpro/debug.cpp"
    ,"common/src/libuniqbpro/ksvdmpc.cpp"
    ,"common/src/libuniqbpro/redis-pool.cpp"
    ,"common/src/libuniqbpro/redis-client.cpp"
    ,"common/src/libuniqbpro/data-factory.cpp"
    ,"common/src/libuniqbpro/redis-lib.cpp"
    ,"common/src/libuniqbpro/env.cpp"
    ,"common/src/libuniqbpro/vuser.cpp"
    ,"common/src/libuniqbpro/util.cpp"
    ,"common/src/libuniqbpro/auth.cpp"
    ,"common/src/libuniqbpro/file.cpp"
    ,"common/src/libuniqbpro/sys.cpp"
    ,"common/src/libuniqbpro/sys2.cpp"
    ,"common/src/libuniqbpro/tcp.cpp"
    ,"common/src/libuniqbpro/unix.cpp"
    ,"common/src/libuniqbpro/err.cpp"
    ,"common/src/libuniqbpro/copy.cpp"
    )

target("uniqbpro_s")
    set_kind("static")
    -- add_cxflags("-g" ,"-Wall" ,"-fno-strict-aliasing" ,"-D_GNU_SOURCE" ,"-D_FILE_OFFSET_BITS=64" ,"-DPTHREAD_STACK_MIN=0" ,"-D_LARGEFILE_SOURCE", {force = true})
    add_links(
        "boost_log", "boost_thread", "boost_filesystem")
    add_files(
    "common/src/libuniqbpro/aes.cpp"
    ,"common/src/libuniqbpro/http_client.cpp"
    ,"common/src/libuniqbpro/tcp-relay.cpp"
    ,"common/src/libuniqbpro/timezone.cpp"
    ,"common/src/libuniqbpro/debug.cpp"
    ,"common/src/libuniqbpro/ksvdmpc.cpp"
    ,"common/src/libuniqbpro/redis-pool.cpp"
    ,"common/src/libuniqbpro/redis-client.cpp"
    ,"common/src/libuniqbpro/data-factory.cpp"
    ,"common/src/libuniqbpro/redis-lib.cpp"
    ,"common/src/libuniqbpro/env.cpp"
    ,"common/src/libuniqbpro/vuser.cpp"
    ,"common/src/libuniqbpro/util.cpp"
    ,"common/src/libuniqbpro/auth.cpp"
    ,"common/src/libuniqbpro/file.cpp"
    ,"common/src/libuniqbpro/sys.cpp"
    ,"common/src/libuniqbpro/sys2.cpp"
    ,"common/src/libuniqbpro/tcp.cpp"
    ,"common/src/libuniqbpro/unix.cpp"
    ,"common/src/libuniqbpro/err.cpp"
    ,"common/src/libuniqbpro/copy.cpp"

    ,"common/src/libuniqbpro/events.cpp"
    ,"common/src/libuniqbpro/uniqbprod.cpp"
    ,"common/src/libuniqbpro/ksvdcm.cpp"
    ,"common/src/libuniqbpro/ksvd-net.cpp"
    ,"common/src/libuniqbpro/vidmodes.cpp"
    ,"common/src/libuniqbpro/sessions.cpp"
    ,"common/src/libuniqbpro/session-cleanup.cpp"
    ,"common/src/libuniqbpro/session-ops.cpp"
    ,"common/src/libuniqbpro/session-state.cpp"
    ,"common/src/libuniqbpro/ticket.cpp"
    ,"common/src/libuniqbpro/machtype.cpp"
    ,"common/src/libuniqbpro/map.cpp"
    ,"common/src/libuniqbpro/provtab.cpp"
    ,"common/src/libuniqbpro/leaf-repo.cpp"
    ,"common/src/libuniqbpro/usb.cpp"
    ,"common/src/libuniqbpro/fs-time.cpp"
    ,"common/src/libuniqbpro/encrypt.cpp"
    ,"common/src/libuniqbpro/pubaddr.cpp"
    ,"common/src/libuniqbpro/applayer-deploy.cpp"
    ,"common/src/libuniqbpro/branch.cpp"
    ,"common/src/libuniqbpro/pool-provision.cpp"
    ,"common/src/libuniqbpro/leaf-provision.cpp"
    ,"common/src/libuniqbpro/leaf.cpp"
    ,"common/src/libuniqbpro/sha.cpp"
    ,"common/src/libuniqbpro/dt-provision.cpp"
    ,"common/src/libuniqbpro/deploy.cpp"
    ,"common/src/libuniqbpro/reply.cpp"
    ,"common/src/libuniqbpro/request_parser.cpp"
    ,"common/src/libuniqbpro/https_server.cpp"
    ,"common/src/libuniqbpro/http_server.cpp"
    ,"common/src/libuniqbpro/disk-image.cpp"
    ,"common/src/libuniqbpro/gow3.cpp"
    ,"common/src/libuniqbpro/qcow2.cpp"
    ,"common/src/libuniqbpro/netiface.cpp"
    ,"common/src/libuniqbpro/alerts.cpp"
    ,"common/src/libuniqbpro/eth_linux.cpp"
    ,"common/src/libuniqbpro/tracker.cpp"
    ,"common/src/libuniqbpro/memstats.cpp"
    ,"common/src/libuniqbpro/html-writer.cpp"
    ,"common/src/libuniqbpro/ancestortab.cpp"
    ,"common/src/libuniqbpro/ksvd-messagequeue.cpp"
    ,"common/src/libuniqbpro/usb-common.cpp"
    ,"common/src/libuniqbpro/pci-common.cpp"
    )

target("ksvdsmart")
    set_kind("static")
    add_files("src/libksvdsmart/*.cpp")

target("uniqbprod")
    set_kind("binary")
    add_files("src/uniqbprod/*.cpp")
    add_deps("uniqbpro_s")
    add_links("jsoncpp"
        ,"pci"
        ,"ssl" ,"crypto" ,"crypt"
        ,"boost_system"
        ,"hiredis"
        ,"jsoncpp"
        ,"rabbitmq"
        )
    add_linkdirs("lib/boost/libs/64-bit/")
    add_defines("PRGNAME=\"uniqbprod\"")

target("ksvdoem-gen")
    set_kind("binary")
    add_files("src/ksvd-cmd/ksvdoem-gen.cpp")
    -- after_build(function (target)
    --     -- FIXME: 放到其他目录，没必要每次都生成这个文件, clean要删除该文件
    --     local buildvm = target:targetfile()
    --     os.execv(buildvm, {}, {stdout = "src/ksvd-cmd/ksvdoem.h"})
    -- end)

target("ksvdoem-header")
    set_policy("build.across_targets_in_parallel", false)
    add_deps('ksvdoem-gen')
    on_build(function (target)
        local buildvm = target:deps()['ksvdoem-gen']:targetfile()
        local outputdir = target:objectdir()
        if not os.isdir(outputdir) then
            os.mkdir(outputdir)
        end
        local header_h = path.join(outputdir, 'ksvdoem.h')
        os.execv(buildvm, {}, {stdout = header_h})
    end)

target("ksvdoem")
    set_kind("shared")
    add_files("src/ksvd-cmd/ksvdoem.c")
    add_deps("ksvdoem-header")
    before_build_files(function(target, sourcefiles)
        local inc_dir = target:deps()['ksvdoem-header']:objectdir()
        target:add("includedirs", inc_dir)
    end)

target("ksvdcmd")
    before_build(function (target)
        -- os.runv('cd src/ksvd-cmd && make ksvdoem.h libksvdoem.so')
        os.run('pwd')
    end)
    set_kind("binary")
    add_defines("COPYRIGHTMSG=\"Copyright 2006-2024 Hunan Kylin Information Engineering Technology Co.,Ltd. All Rights Reserved.\"")
    add_files("src/ksvd-cmd/*.cpp")
    remove_files("src/ksvd-cmd/ksvdoem-gen.cpp")
    add_deps("uniqbpro_s")
    add_deps("ksvdoem-header")
    add_links("jsoncpp"
        ,"ssl" ,"crypto" ,"crypt"
        ,"boost_system"
        ,"hiredis"
        ,"jsoncpp"
        ,"rabbitmq"
        )
    add_linkdirs("lib/boost/libs/64-bit/")
    add_defines("PRGNAME=\"ksvdcmd\"")
    before_build_files(function(target, sourcefiles)
        local inc_dir = target:deps()['ksvdoem-header']:objectdir()
        target:add("includedirs", inc_dir)
    end)

target("ksvd-util")
    set_kind("binary")
    add_files("src/ksvd-util/*.cpp")
    add_deps("uniqbpro_s")
    add_deps("ksvdsmart")
    add_links("jsoncpp"
        ,"ssl" ,"crypto" ,"crypt"
        ,"boost_system"
        ,"boost_program_options"
        ,"boost_regex"
        ,"hiredis"
        ,"jsoncpp"
        ,"rabbitmq"
        )
    add_linkdirs("lib/boost/libs/64-bit/")
    add_defines("PRGNAME=\"ksvd-util\"")

target("ksvd-img")
    set_kind("binary")
    add_files("src/ksvd-img/*.cpp")
    add_deps("uniqbpro_s")
    add_links("jsoncpp"
        ,"ssl" ,"crypto" ,"crypt"
        ,"boost_system" ,"boost_program_options"
        ,"hiredis"
        ,"jsoncpp"
        )
    add_linkdirs("lib/boost/libs/64-bit/")
    add_defines("PRGNAME=\"ksvd-img\"")


target("uniqb-runtime-server")
    set_kind("binary")
    add_defines("COPYRIGHTMSG=\"Copyright 2006-2024 Hunan Kylin Information Engineering Technology Co.,Ltd. All Rights Reserved.\"")
    add_defines("PRODNAME=\"uniqb-runtime-server\"")
    add_files("src/uniqb-runtime-server/*.cpp")
    add_deps("uniqbpro_s")
    add_links("jsoncpp"
        ,"pci"
        ,"ssl" ,"crypto" ,"crypt"
        ,"boost_system"
        ,"hiredis"
        ,"jsoncpp"
        ,"virt", "virt-qemu"
        )
    add_linkdirs("lib/boost/libs/64-bit/")
    add_defines("PRGNAME=\"uniqb-runtime-server\"")
