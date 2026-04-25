# 飞书 OpenAPI 速查

> 给 lib_feishu.py 维护者用，普通调用者不需要看。

## Base URL

```
https://open.feishu.cn/open-apis
```

## 鉴权

### 自建应用获取 tenant_access_token

```http
POST /auth/v3/tenant_access_token/internal
Content-Type: application/json

{
  "app_id": "cli_xxx",
  "app_secret": "yyy"
}
```

响应：
```json
{
  "code": 0,
  "msg": "ok",
  "tenant_access_token": "t-xxxx",
  "expire": 7200
}
```

后续所有 API 加 header：
```
Authorization: Bearer t-xxxx
```

## Drive: 上传文件

```http
POST /drive/v1/files/upload_all
Content-Type: multipart/form-data

fields:
  file_name: clash-guide.md
  parent_type: explorer        (云空间) 或 docx_file (文档附件)
  parent_node: <folder_token>  (留空可能报错)
  size: <字节数>
  file: <文件二进制>
```

响应：
```json
{
  "code": 0,
  "data": { "file_token": "boxbcxxx" }
}
```

> 注意：`parent_type=explorer` 必须有 `parent_node`（文件夹 token）。
> 如果想推到「我的空间」根目录，需要先调 `GET /drive/v1/files?parent_token=root` 拿根目录 token。
> 或者用 import 任务时 mount_type=1 + mount_key 留空，飞书会自动放到默认位置。

## Drive: Markdown 导入

### 创建任务

```http
POST /drive/v1/import_tasks
Content-Type: application/json

{
  "file_extension": "md",
  "file_token": "boxbcxxx",
  "type": "docx",
  "file_name": "clash-guide",
  "point": {
    "mount_type": 1,
    "mount_key": ""
  }
}
```

`mount_type`:
- `1` = 我的空间（个人）
- `2` = 知识库（wiki）

响应：
```json
{
  "code": 0,
  "data": { "ticket": "7123456789" }
}
```

### 查询任务

```http
GET /drive/v1/import_tasks/{ticket}
```

响应：
```json
{
  "code": 0,
  "data": {
    "result": {
      "ticket": "7123456789",
      "type": "docx",
      "job_status": 0,
      "token": "doxbcyyy",
      "url": "https://xxx.feishu.cn/docx/doxbcyyy"
    }
  }
}
```

`job_status`:
- `0` = 成功（v2 API 用此值）
- `1` = 进行中
- `2` = 成功（旧 API 用此值，部分场景仍存在）
- `>=3` = 失败

> 实测某些环境 0=success，某些 2=success。`wait_import_done` 同时支持。

## Docx: 文档块

### 列出 blocks

```http
GET /docx/v1/documents/{doc_id}/blocks?page_size=500&page_token=
```

响应：
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "block_id": "doxxxxx",
        "parent_id": "",
        "block_type": 1,
        "page": { ... },
        "children": [...]
      },
      ...
    ],
    "has_more": false,
    "page_token": ""
  }
}
```

### 删除子 block

```http
DELETE /docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children/batch_delete
Content-Type: application/json

{
  "start_index": 0,
  "end_index": 10
}
```

> 注意：是 `[start, end)` 半开区间。删 5 个 = `start=0, end=5`。

### 插入子 block

```http
POST /docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children
Content-Type: application/json

{
  "children": [
    {
      "block_type": 4,
      "heading1": {
        "elements": [{"text_run": {"content": "标题"}}]
      }
    },
    ...
  ],
  "index": 0
}
```

`block_type` 常用：
- `1` = page（顶层，不能直接造）
- `2` = text（段落）
- `4` = heading1
- `5` = heading2
- `6` = heading3
- `12` = bullet list
- `13` = numbered list
- `14` = code
- `15` = quote
- `16` = todo
- `27` = divider
- `31` = table

> 完整 block_type 见 https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/data-structure/block

## 错误码

| code | 含义 | 处理 |
| --- | --- | --- |
| 0 | 成功 | - |
| 99991661 | 频率限制 | 重试，加退避 |
| 99991663 | app_secret 错误 | 提示用户 |
| 99991668 | token 失效 | 自动重新获取 |
| 99991672 | 应用未发布 | 提示用户去发布 |
| 1061002 | 无权操作 | 提示用户加协作者 |
| 1069902 | 文档不存在 | 检查 doc_id |

## 频率限制

- 一般 API：100 QPS
- import 任务：30 QPS
- 上传：50 QPS

我们的脚本调用远低于此，无需特别处理。

## 文档参考

- 总览: https://open.feishu.cn/document/server-docs/docs/docs-overview
- Drive: https://open.feishu.cn/document/server-docs/docs/drive-v1/upload/upload-overview
- Docx: https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/get
- Import: https://open.feishu.cn/document/server-docs/docs/drive-v1/import_task/create
