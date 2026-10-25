# 更新现有 Workshop 条目的分类标签

`scripts/update_workshop_tags.py` 是所有 EU5 模组工作区共用的标签工具。它读取明确指定的 metadata，将 `tags` 同步到明确指定的已有 Steam Workshop 条目。默认只预览；不需要 API key、密码或额外 Python 包。

## 使用

先设置 `$env:EU5_PYTHON` 为本机 `eu5` 环境中 64 位 `python.exe` 的绝对路径，保持 Steam 登录条目的原始发布账号。在挂载此仓库的模组工作区运行：

```powershell
$env:PYTHONUTF8 = '1'
# 将这两个值替换为自己的已有条目 ID 和 metadata 文件。
$workshopItemId = '1234567890'
$modMetadata = 'src/my_mod/.metadata/metadata.json'

# 离线预览，不连接 Steam
& $env:EU5_PYTHON .eu5-base/scripts/update_workshop_tags.py --item-id $workshopItemId --metadata $modMetadata

# 读取条目标题、当前分类、增删差异和账号归属，不提交
& $env:EU5_PYTHON .eu5-base/scripts/update_workshop_tags.py --item-id $workshopItemId --metadata $modMetadata --check

# 用 metadata 中的完整 tags 列表替换远端分类，然后读回验证
& $env:EU5_PYTHON .eu5-base/scripts/update_workshop_tags.py --item-id $workshopItemId --metadata $modMetadata --apply
```

在 `eu5-modding-base` 仓库直接运行时，将脚本路径改为 `scripts/update_workshop_tags.py`，传入目标工作区 metadata 的绝对路径。

共享入口强制要求 `--metadata` 和 `--item-id`，不会猜测项目、发布目标或条目。相对 metadata 路径以调用时的当前目录为准；绝对路径可从任意目录使用。项目可以保留薄入口，为本项目补上默认 metadata，但不复制实现。工具不创建新条目，标签已一致时不提交。

## 分类与安装路径

这是完整替换，会移除 metadata 列表之外的原有标签。通过 Steam 注册表、默认目录及 `libraryfolders.vdf` 查找游戏；也支持 `EU5_GAME_DIR` 或 `--game-dir 'D:\SteamLibrary\steamapps\common\Europa Universalis V'`。路径可指向安装根目录或其 `game` 子目录。

在线模式使用安装版本的 `game/main_menu/create_mod_tags.json` 验证分类；离线预览使用本共享仓库的 `reference_game_files/game/main_menu/create_mod_tags.json`。空列表、重复、拼写不匹配、非 EU5 metadata 都会被拒绝。调用方不用复制分类清单。

## 修改范围与结果

只提交 `SetItemTags`，不设置标题、介绍、可见性、封面、内容文件或更新日志。不修改本地 metadata，不调用项目构建脚本，不上传源文件。

提交前检查条目属于 EU5，且当前账号是原始所有者（协作者账号会被此工具拒绝）。提交后必须收到成功结果，再读取分类并对比；同时核对标题、介绍、可见性、所有者和内容/封面句柄没有变化。只有完整验证通过才输出 `Verified`。程序不根据本地名称猜测条目 ID。

请求默认超时 60 秒，可用 `--timeout` 调整到最多 300 秒。如果提交后超时或读回失败，远端可能已经更新；先用 `--check` 确认，不自动重试提交。若 Steam 要求同意 Workshop 协议，由用户在 Steam 中查看处理。

## 环境与验证

- 在线操作要求 Windows x64 与 64 位 Python，使用本机 EU5 的 `binaries/steam_api64.dll`；不下载或分发 DLL。
- 当前绑定已核对为 `SteamUGC_v016`、`SteamUtils_v010`、`SteamUser_v021`。游戏更新导致接口变化时会报错退出，需要重新核对 SDK，不能猜测 ABI。
- 在临时目录放置 `steam_appid.txt`，结束后清理，并恢复工作目录及进程环境变量；不往游戏目录写文件。
- Steam 必须运行、在线，并拥有 EU5。若 `SteamAPI_Init` 失败，先在普通 PowerShell 运行；代理沙箱可能无法访问 Steam IPC，即使 Steam 进程存在。不要通过复制 DLL 到任意目录或修改 Steam 安全配置解决。
- 自动回归：在共享仓库运行 `& $env:EU5_PYTHON scripts/test_update_workshop_tags.py`，或在模组工作区运行 `.eu5-base/scripts/test_update_workshop_tags.py`。这些测试不写入 Steam。

## 原理与来源

社区工具的 `-wp` 模式同时更新标题、介绍和标签。本工具独立实现较窄的流程：`StartItemUpdate` → `SetItemTags` → `SubmitItemUpdate`，通过异步结果及新查询验证完成，不复制社区工具源码。

- [社区上传工具说明](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-toolkit/wiki/Upload-Tool)
- [Steam 官方 UGC 接口](https://partner.steamgames.com/doc/api/ISteamUGC#SetItemTags)
- [Steam API 初始化说明](https://partner.steamgames.com/doc/api/steam_api#SteamAPI_Init)
- [Valve SDK 1.53 头文件镜像，固定提交](https://github.com/rlabrecque/SteamworksSDK/blob/041035277782/public/steam/isteamugc.h)：用于核对当前 DLL 的参数、结构体及回调布局。最新 SDK 的 `SetItemTags` 签名已有变化，因此不套用最新版 ABI。

本地 JSON 标签与 Workshop 分类是两个需要同步的状态。二者不一致不能证明游戏上传器具体在哪一步漏了同步。项目条目 ID、账号检查结果及发布记录应留在对应工作区。
