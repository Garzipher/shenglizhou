# 周圣力 · 个人主页

展示个人简介、教育背景、工作经历与项目实践，提供中英文简历在线预览和 PDF 下载。

[访问网站](https://garzipher.github.io/shenglizhou/) · [English](https://garzipher.github.io/shenglizhou/en/) · [查看简历](https://garzipher.github.io/shenglizhou/resume.html)

## 网站内容

- **关于**：个人简介、教育背景与经历概览。
- **技能与奖项**：专业技能与语言能力。
- **项目**：项目背景、技术方案与实践内容。
- **经历**：工作经历与主要职责。
- **简历**：中英文 PDF 下载与在线预览。

## 技术与体验

使用 HTML、CSS 和原生 JavaScript 构建静态网站，通过 GitHub Pages 发布。

- 中英文页面一一对应，支持切换语言。
- 适配桌面和移动设备。
- 站内导航支持页面缓存和预取。
- 图片优先采用无损 WebP，并提供 PNG 回退。
- 静态资源使用内容哈希版本标记。

## 本地预览

在仓库根目录运行：

    python -m http.server 8765 --bind 127.0.0.1 --directory site

浏览器打开 http://127.0.0.1:8765/ 。

## 项目结构

    site/                       网站文件
      en/                       英文页面
      files/                    简历 PDF
      licenses/                 第三方许可文件
    .github/workflows/pages.yml GitHub Pages 部署配置

## 部署

仓库使用 main 分支，通过 GitHub Actions 将 site/ 目录发布到 GitHub Pages。站点文件或部署配置更新后自动部署。

## 许可说明

第三方组件与主题的许可信息见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 [site/licenses/](site/licenses/)。个人资料、照片及简历的权利归本人所有。
