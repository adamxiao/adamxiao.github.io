#include "qemu/osdep.h"
#include "block/block_int.h"
#include <hiredis/hiredis.h>
#include "block/qdict.h"
#include "qapi/error.h"
#include "qemu/module.h"
#include "qemu/option.h"
/*#include "qemu/cutils.h"*/

#include <stdint.h>
#include <string.h>

typedef struct RedisDriverState {
    redisContext *context;
    char *key;
} RedisDriverState;

static coroutine_fn int redis_co_preadv(BlockDriverState *bs, uint64_t offset, uint64_t bytes,
                                        QEMUIOVector *qiov, int flags)
{
    RedisDriverState *s = bs->opaque;
    redisReply *reply = redisCommand(s->context, "GET %s", s->key);
    if (reply == NULL || reply->type != REDIS_REPLY_STRING) {
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    size_t available_bytes = reply->len - offset;
    if (available_bytes < bytes) {
        bytes = available_bytes;
    }

    // 将数据拷贝到 QEMUIOVector 中
    qemu_iovec_from_buf(qiov, 0, reply->str + offset, bytes);
    freeReplyObject(reply);
    return bytes;
}


static coroutine_fn int redis_co_pwritev(BlockDriverState *bs, uint64_t offset, uint64_t bytes,
                                         QEMUIOVector *qiov, int flags)
{
    RedisDriverState *s = bs->opaque;

    // 获取当前数据
    redisReply *reply = redisCommand(s->context, "GET %s", s->key);
    if (reply == NULL || reply->type != REDIS_REPLY_STRING) {
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    // 计算新的数据长度，合并数据
    size_t current_size = reply->len;
    size_t new_size = offset + bytes > current_size ? offset + bytes : current_size;
    char *new_data = g_malloc0(new_size);
    memcpy(new_data, reply->str, current_size);
    qemu_iovec_to_buf(qiov, 0, new_data + offset, bytes);
    freeReplyObject(reply);

    // 将修改后的数据写回 Redis
    reply = redisCommand(s->context, "SET %s %b", s->key, new_data, new_size);
    g_free(new_data);

    if (!reply || reply->type == REDIS_REPLY_ERROR) {
        if (reply) freeReplyObject(reply);
        return -EIO;
    }
    freeReplyObject(reply);

    return bytes;
}

// 定义协议驱动：用于注册 `redis://` 协议
static int redis_protocol_open(BlockDriverState *bs, QDict *options, int flags, Error **errp) {
    RedisDriverState *s = bs->opaque;
    const char *hostname = qdict_get_try_str(options, "host");
    int port = qdict_get_int(options, "port");

    s->context = redisConnect(hostname, port);
    if (s->context == NULL || s->context->err) {
        if (s->context) {
            error_setg(errp, "Redis connection error: %s", s->context->errstr);
            redisFree(s->context);
        } else {
            error_setg(errp, "Redis connection error: can't allocate redis context");
        }
        return -EIO;
    }

    s->key = g_strdup(qdict_get_try_str(options, "key"));
    return 0;
}

static void redis_protocol_close(BlockDriverState *bs) {
    RedisDriverState *s = bs->opaque;
    redisFree(s->context);
    g_free(s->key);
}

static int qcow2_redis_file_open(BlockDriverState *bs, QDict *options, int flags, Error **errp) {
    // 提取并检查 filename 参数
    const char *filename = qdict_get_try_str(options, "filename");
    if (!filename || strncmp(filename, "redis://", 8) != 0) {
        error_setg(errp, "Invalid filename: must start with redis://");
        return -EINVAL;
    }

    RedisDriverState *s = g_new0(RedisDriverState, 1);
    bs->opaque = s;
    qdict_del(options, "filename"); // 参考qemu_rbd_open

    // 解析 redis://hostname:port/key 格式的 URL
    const char *hostname = "localhost";
    int port = 6379;
    const char *key = filename + 8;  // 跳过 "redis://"
    
    char *colon = strchr(key, ':');
    if (colon) {
        hostname = g_strndup(key, colon - key);
        port = atoi(colon + 1);
        key = strchr(colon, '/') + 1;
    }
    s->key = g_strdup(key);

    // 连接 Redis
    s->context = redisConnect(hostname, port);
    if (s->context == NULL || s->context->err) {
        error_setg(errp, "Failed to connect to Redis at %s:%d", hostname, port);
        g_free(s->key);
        g_free(s);
        return -EIO;
    }

    return 0;
}


// 实现 bdrv_co_create 函数
static coroutine_fn int redis_co_create(BlockdevCreateOptions *opts, Error **errp) {
    // 确保传入的 opts 是一个 QCOW2 格式的 Redis 镜像创建选项
    if (opts->driver != BLOCKDEV_DRIVER_QCOW2) {
        error_setg(errp, "Redis driver only supports QCOW2 format.");
        return -EINVAL;
    }
    
    // 获取文件名和大小
    /*BlockdevCreateOptionsQcow2 *qcow2_opts = opts->qcow2;*/
    BlockdevCreateOptionsQcow2 *qcow2_opts = &opts->u.qcow2;

    /*const char *filename = qcow2_opts->filename;*/
    const char *filename = "my-qcow2-image"; // TODO:
    int64_t size = qcow2_opts->size;
(void)size;

    // 解析 filename 并连接到 Redis
    const char *hostname = "localhost";
    int port = 6379;
    const char *key = filename + 8;  // 假设格式为 "redis://hostname:port/key"

    char *colon = strchr(key, ':');
    if (colon) {
        hostname = g_strndup(key, colon - key);
        port = atoi(colon + 1);
        key = strchr(colon, '/') + 1;
    }

    // 连接 Redis
    redisContext *context = redisConnect(hostname, port);
    if (context == NULL || context->err) {
        error_setg(errp, "Failed to connect to Redis at %s:%d", hostname, port);
        return -EIO;
    }

    // 初始化 QCOW2 头部（根据 QCOW2 规范填充必要的头部信息）
    uint8_t qcow2_header[512] = {0};
    qcow2_header[0] = 'Q';
    qcow2_header[1] = 'F';
    qcow2_header[2] = 'I';
    qcow2_header[3] = 0xfb;

    // 将头部数据写入 Redis
    redisReply *reply = redisCommand(context, "SET %s %b", key, qcow2_header, sizeof(qcow2_header));
    if (!reply || reply->type == REDIS_REPLY_ERROR) {
        error_setg(errp, "Failed to create image in Redis: %s", context->errstr);
        redisFree(context);
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    freeReplyObject(reply);
    redisFree(context);
    return 0;
}


// 实现 bdrv_co_create_opts 函数
static coroutine_fn int redis_co_create_opts(const char *filename,
                                                QemuOpts *opts,
                                                Error **errp) {
    /* Read out options */
    uint64_t size = ROUND_UP(qemu_opt_get_size_del(opts, BLOCK_OPT_SIZE, 0),
                              BDRV_SECTOR_SIZE);
    (void)size;

// TODO: 相关参数获取错误了!

    if (!filename) {
        error_setg(errp, "Filename must be specified for Redis image creation.");
        return -EINVAL;
    }

printf("adam-debug create_opts filename is %s\n", filename);
    
    // 解析 filename 并连接到 Redis
    const char *hostname = "localhost";
    int port = 6379;
    const char *key = filename + 8;  // 假设格式为 "redis://hostname:port/key"

    char *colon = strchr(key, ':');
    if (colon) {
        hostname = g_strndup(key, colon - key);
        port = atoi(colon + 1);
        key = strchr(colon, '/') + 1;
    }
    /*key = "my-qcow2-image";*/

    // 连接到 Redis
    redisContext *context = redisConnect(hostname, port);
    if (context == NULL || context->err) {
        error_setg(errp, "Failed to connect to Redis at %s:%d", hostname, port);
        return -EIO;
    }

    // 初始化 QCOW2 头部（根据 QCOW2 规范填充必要的头部信息）
    uint8_t qcow2_header[512] = {0};
    qcow2_header[0] = 'Q';
    qcow2_header[1] = 'F';
    qcow2_header[2] = 'I';
    qcow2_header[3] = 0xfb;

    printf("adam-debug create redis key is %s\n", key);

    // 在 Redis 中写入头部数据
    redisReply *reply = redisCommand(context, "SET %s %b", key, qcow2_header, sizeof(qcow2_header));
    if (!reply || reply->type == REDIS_REPLY_ERROR) {
        error_setg(errp, "Failed to create image in Redis: %s", context->errstr);
        redisFree(context);
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    freeReplyObject(reply);
    redisFree(context);
    return 0;
}


static QemuOptsList qemu_redis_create_opts = {
    .name = "rbd-create-opts",
    .head = QTAILQ_HEAD_INITIALIZER(qemu_redis_create_opts.head),
    .desc = {
        {
            .name = BLOCK_OPT_SIZE,
            .type = QEMU_OPT_SIZE,
            .help = "Virtual disk size"
        },
        {
            .name = BLOCK_OPT_CLUSTER_SIZE,
            .type = QEMU_OPT_SIZE,
            .help = "RBD object size"
        },
        { /* end of list */ }
    }
};


// 实现 bdrv_co_truncate 函数
static int coroutine_fn qemu_redis_co_truncate(BlockDriverState *bs,
                                             int64_t offset,
                                             PreallocMode prealloc,
                                             Error **errp) {
    // 验证 BlockDriverState 的有效性和连接
    RedisDriverState *s = bs->opaque;
    if (!s->context) {
        error_setg(errp, "Redis connection is not initialized.");
        return -ENOTCONN;
    }

    printf("adam-debug redis key is %s\n", s->key);

    // 根据 QCOW2 规范更新镜像大小
    uint8_t qcow2_header[512];
    redisReply *reply = redisCommand(s->context, "GET %s", s->key);
    if (!reply || reply->type == REDIS_REPLY_NIL || reply->type == REDIS_REPLY_ERROR) {
        error_setg(errp, "Failed to read image header from Redis.");
        if (reply) freeReplyObject(reply);
        return -EIO;
    }
    memcpy(qcow2_header, reply->str, sizeof(qcow2_header));
    freeReplyObject(reply);

    // 更新大小字段（根据 QCOW2 文件格式规范填充新大小）
    // 例如：将 offset 赋值给 QCOW2 头部的大小字段
    // *(int64_t *)&qcow2_header[QCOW2_SIZE_OFFSET] = offset;

    // 将更新后的头部写回 Redis
    reply = redisCommand(s->context, "SET %s %b", s->key, qcow2_header, sizeof(qcow2_header));
    if (!reply || reply->type == REDIS_REPLY_ERROR) {
        error_setg(errp, "Failed to update image size in Redis.");
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    freeReplyObject(reply);
    return 0;
}


// 获取磁盘大小
static int64_t qemu_redis_getlength(BlockDriverState *bs) {
    /*RedisProtocolState *s = bs->opaque;*/
    RedisDriverState *s = bs->opaque;
    if (!s->context) {
        return -ENOTCONN;
    }

    printf("adam-debug qemu_redis_getlength key is %s\n", s->key);

    // 获取 Redis 中存储的镜像大小（假设 Redis 中保存了实际的大小信息）
    redisReply *reply = redisCommand(s->context, "STRLEN %s", s->key);
    if (!reply || reply->type == REDIS_REPLY_NIL || reply->type == REDIS_REPLY_ERROR) {
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    // 假设 Redis 中存储的大小信息是整数类型的磁盘大小
    int64_t size = reply->integer;
    freeReplyObject(reply);


    printf("adam-debug qemu_redis_getlength size is %u\n", (unsigned)size);

    return size;
}

static int qemu_redis_getinfo(BlockDriverState *bs, BlockDriverInfo *bdi)
{
    /*RedisProtocolState *s = bs->opaque;*/
    RedisDriverState *s = bs->opaque;
    if (!s->context) {
        return -ENOTCONN;
    }

    printf("adam-debug qemu_redis_getinfo key is %s\n", s->key);

    // 获取 Redis 中存储的镜像大小（假设 Redis 中保存了实际的大小信息）
    redisReply *reply = redisCommand(s->context, "STRLEN %s", s->key);
    if (!reply || reply->type == REDIS_REPLY_NIL || reply->type == REDIS_REPLY_ERROR) {
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    bdi->cluster_size = 65535;

    // 假设 Redis 中存储的大小信息是整数类型的磁盘大小
    freeReplyObject(reply);

    return 0;
}


static int64_t qemu_redis_allocated_file_size(BlockDriverState *bs)
{
    /*RedisProtocolState *s = bs->opaque;*/
    RedisDriverState *s = bs->opaque;
    if (!s->context) {
        return -ENOTCONN;
    }

    printf("adam-debug qemu_redis_allocated_file_size key is %s\n", s->key);

    // 获取 Redis 中存储的镜像大小（假设 Redis 中保存了实际的大小信息）
    redisReply *reply = redisCommand(s->context, "STRLEN %s", s->key);
    if (!reply || reply->type == REDIS_REPLY_NIL || reply->type == REDIS_REPLY_ERROR) {
        if (reply) freeReplyObject(reply);
        return -EIO;
    }

    // 假设 Redis 中存储的大小信息是整数类型的磁盘大小
    int64_t size = reply->integer;
    freeReplyObject(reply);

    printf("adam-debug qemu_redis_allocated_file_size size is %u\n", (unsigned)size);

    return size;
}


// 注册驱动
BlockDriver bdrv_redis = {
    .format_name = "redis",
    .protocol_name      = "redis",
    .instance_size = sizeof(RedisDriverState),
    .bdrv_file_open     = qcow2_redis_file_open,

    .bdrv_open = redis_protocol_open,
    .bdrv_close = redis_protocol_close,

    .bdrv_get_info          = qemu_redis_getinfo,
    .bdrv_getlength         = qemu_redis_getlength,
    .bdrv_get_allocated_file_size = qemu_redis_allocated_file_size,

    .bdrv_co_preadv = redis_co_preadv,  // 异步读
    .bdrv_co_pwritev = redis_co_pwritev, // 异步写

    .bdrv_co_create   = redis_co_create,  // 使用协程接口
    .bdrv_co_create_opts    = redis_co_create_opts, // 验证发现使用这个接口创建的
    .create_opts            = &qemu_redis_create_opts,

    .bdrv_co_truncate       = qemu_redis_co_truncate, // resize支持
};


static void bdrv_redis_init(void) {
    bdrv_register(&bdrv_redis);
}

block_init(bdrv_redis_init);
