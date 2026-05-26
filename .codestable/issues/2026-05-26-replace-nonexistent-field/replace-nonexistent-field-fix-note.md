---
doc_type: issue-fix
issue: 2026-05-26-replace-nonexistent-field
status: resolved
---

# dataclasses.replace 传了非字段属性导致 TypeError — Fix Note

## 1. 根因

`freebuff2api/codebuff.py:645` 中 `dataclasses.replace(settings, codebuff_token=token)` 试图替换 `Settings` 的一个字段，但 `Settings`（`frozen=True` dataclass）仅声明了复数字段 `codebuff_tokens: tuple[str, ...]`；`codebuff_token` 是同名 `@property`（只读、无 setter），并非 dataclass 字段。`dataclasses.replace()` 只能替换 dataclass 声明的字段，因此引发：

```
TypeError: Settings.__init__() got an unexpected keyword argument 'codebuff_token'. Did you mean: 'codebuff_tokens'?
```

## 2. 修复方案

将 `replace(settings, codebuff_token=token)` 改为：

```python
replace(settings, codebuff_tokens=(token,) if token else ())
```

用单元素 tuple 替换实际存在的 `codebuff_tokens` 字段。当 `token` 为 `None` 时传空 tuple，使 `codebuff_token` property 正确返回 `None`。

## 3. 修改文件

- `freebuff2api/codebuff.py:645`

## 4. 验证

- [x] **复现步骤验证**：模拟 `dataclasses.replace` 替换 `codebuff_tokens`，不再抛 `TypeError`
- [x] **期望行为验证**：`replace` 后 `Settings.codebuff_token` property 正常取到第一个 token；空 tuple 时返回 `None`
- [x] **影响面回归**：`CodebuffAccountPool` 初始化路径测试通过，账号池构造无异常

## 5. 顺手发现

无。

## 6. 提交说明

```
fix: 修复 dataclasses.replace 使用非 dataclass 字段报错

Settings 中 codebuff_token 是 property，不能传给 replace。
改用实际存在的 codebuff_tokens 字段，将单 token 包成 tuple。
```
