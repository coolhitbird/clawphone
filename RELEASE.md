# ClawPhone 发布指南

## ✅ 已完成

- [x] 代码开发 (adapter, examples, tests)
- [x] 单元测试通过 (test_clawphone.py)
- [x] 文档撰写 (SKILL.md, README.md)
- [x] 目录结构就绪

---

## 🚀 待执行发布步骤

### 1. 创建 GitHub 仓库

```bash
cd C:\Users\wang20\.openclaw\workspace\skills\clawphone

# 初始化 git
git init
git add .
git commit -m "feat: initial release - ClawPhone ICQ-style instant messaging"

# 创建远程仓库 (在 GitHub 上)
# 访问 https://github.com/new
# Repository name: clawphone
# Description: 让 OpenClaw Agent 拥有"手机号码"——像 ICQ 一样的即时通讯体验
# Choose Public, do NOT initialize with README/.gitignore

# 关联远程并推送
git remote add origin https://github.com/ClawMesh/clawphone.git  # 需替换为您的账号
git branch -M main
git push -u origin main
```

**注意**: 需要 GitHub 账号。建议组织 `ClawMesh` 或您的个人账号下。

---

### 2. 注册到 SkillHub (国内)

```bash
# 确保 skillhub CLI 在 PATH
# 如未安装，参考: https://skillhub.tencent.com/docs

# 登录 (如果未登录)
skillhub login

# 发布
cd C:\Users\wang20\.openclaw\workspace\skills\clawphone
skillhub publish .
```

**预期结果**: Skill 出现在 SkillHub 搜索中，其他用户可以一键安装。

---

### 3. 注册到 ClawHub (国际备用)

```bash
# 如果已安装 clawhub
clawhub publish .
```

---

### 4. 在 InStreet 社区发布介绍

使用 `post.ps1` 发布到 `skills` 板块：

```powershell
.\scripts\post.ps1 `
  -Title "ClawPhone - 让 Agent 拥有手机号码" `
  -Submolt "skills" `
  -Content (Get-Content .\skills\clawphone\README.md -Raw)
```

---

### 5. 更新 MEMORY.md 和 PLAN_TRACKING.md

在 `MEMORY.md` 记录 ClawPhone 开发完成，并加入后续计划。

---

## 📊 检查清单

- [ ] GitHub 仓库创建并推送
- [ ] SkillHub publish 成功
- [ ] ClawHub publish 成功（可选）
- [ ] InStreet 社区发帖
- [ ] 测试安装: `skillhub install clawphone`
- [ ] 运行 examples/quick_demo.py 验证功能

---

## 🐛 已知限制

- 号码簿目前为本地 SQLite，不支持跨设备同步
- 无离线消息缓存（类似于早期 ICQ）
- 需要手动注入 ClawMesh 网络适配器（系统自动完成）

---

**完成日期**: 2026-03-12  
**版本**: 1.0.0  
**开发者**: ClawMesh Team
