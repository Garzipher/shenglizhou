# 周圣力个人简历网站

[中文站](https://garzipher.github.io/Personal_Resume/) · [English](https://garzipher.github.io/Personal_Resume/en/)

个人经历、项目和简历展示网站。沿用 [JIAN Junhao 的个人站](https://junhaojian.github.io/) 的布局、配色和日期样式，使用周圣力本人已确认的资料替换内容。

## 功能

- 中文为默认语言，英文页面位于 site/en/；每页的语言入口切换到另一语言的对应页面。
- 包含简介、技能与奖项、项目、工作经历、简历五组双语页面。
- 分别提供中文、英文的一页 PDF 下载与图片预览。
- 静态 HTML、CSS 和 JavaScript，无构建依赖；语言切换使用普通链接。
- 相对路径适配 GitHub Pages 的 /Personal_Resume/ 子路径。
- 站内链接采用轻量缓存导航：空闲或悬停时预取，点击时更新内容，支持前进/后退和对应页面的语言切换。首次访问仍是完整静态页面，直接打开及刷新任意页面均可使用；脚本不可用时保留普通链接。
- 日期标签直接生成到 HTML；页面不再加载 jQuery、旧主题插件或 Google Fonts。头像和简历预览优先使用无损 WebP，同时保留 PNG 回退。节省流量模式和慢速 2G 连接不主动预取。

## 本地预览

在仓库根目录运行：

    python -m http.server 8765 --bind 127.0.0.1 --directory site

打开 http://127.0.0.1:8765/ 。也可直接打开 site/index.html。

## 部署

仓库仅使用 main 分支。GitHub Pages 在 Settings → Pages 中选择 GitHub Actions。

.github/workflows/pages.yml 在 main 的站点文件变更后执行，只上传 site/，不使用 gh-pages 分支。Actions 已固定到经核对的官方提交 SHA；默认令牌仅有读取权限，发布任务单独授予 pages:write 和 id-token:write。

正式访问地址：https://garzipher.github.io/Personal_Resume/ 。可在 Actions 的 Deploy resume to GitHub Pages 任务中查看部署状态或手动重新运行。此地址属于 Garzipher/Personal_Resume 项目站；没有配置其他 GitHub 用户域名。

## 仓库范围

| 路径 | 用途 |
| --- | --- |
| site/ | 公开网页、样式、脚本、头像、简历 PDF 与预览图 |
| site/en/ | 对应的英文页面 |
| site/licenses/ | 参考站及依赖的许可与版权声明 |
| .github/workflows/pages.yml | 单分支 Pages 发布配置 |
| .gitignore | 采用根目录白名单，阻止本地资料进入仓库 |

原始 Word 简历、副本、参考材料、DOCX 输出、个人资料生成源、缓存、检查截图和密码学习工具均不在 Git 跟踪范围内，也不进入 Pages 发布包。本机的这些资料继续保存在 RESUME 目录下；原始简历不作修改。

## 本机内容维护

本机 RESUME/content/profile.json 与 profile.en.json 分别维护两种语言的事实资料；scripts/build_site.py 生成两套网页。scripts/build_resume.py 和 --en 参数分别生成中文、英文 DOCX；scripts/export_word.ps1 使用 Windows Word 导出 PDF，再运行 scripts/publish_resume_assets.py 同步 PDF 和预览图。上述本地源文件不随这个静态发布仓库上传。

更新后请核对页面语言、日期、导航和两版 PDF。技术名称及产品原名保留原文；英语能力仅表述为“英语四级水平”，不表述为已持有证书。无获奖记录不新增奖项。英文公司名为便于阅读的翻译，不主张其为公司官方英文名称。

本机 scripts/optimize_images.py 由页面构建和简历资源发布流程调用，在 PNG 更新后重新生成无损 WebP；不要只替换 PNG 而保留过期的同名 WebP。快速导航缓存仅存在于当前页面会话内，刷新页面即可获取已部署的最新版本。

RainSoul 的本人参与范围是产品、UI 和 Git 迭代，代码实现和测试由 AI 完成。密码应用学习工具未表述为本人已经完成的职业项目。

## 版权与许可

参考仓库 JunhaoJian/junhaojian.github.io 的 MIT 许可、jQuery 和 Font Awesome 的原始许可随站点分发，详见 THIRD_PARTY_NOTICES.md 及 site/licenses/。原作者的头像、姓名、联系方式、经历及统计代码不在本站中使用。网站中的个人资料、照片和简历不因主题采用 MIT 而自动获得第三方使用授权。
