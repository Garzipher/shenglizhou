# 网站样式与第三方资源来源

参考网站：https://junhaojian.github.io/ ，取得日期：2026-10-22。根据用户明确要求，本地站复用其 DOM 布局、页面内联布局样式、样式表和必要的导航脚本，以便复刻 UI。原作者姓名、头像、联系方式、个人经历、Google Analytics 和搜索引擎验证信息已移除。参考页面只保存在 materials/reference/ 以供核对，不作为本人经历发布。

assets/css/main.css 包含 Font Awesome Free 5.5.0 的原版权声明：图标 CC BY 4.0、字体 SIL OFL 1.1、代码 MIT。下载的 fa-solid-900.woff2 与 fa-brands-400.woff2 用于保持原站图标样式。

jQuery 2.1.3 来自 cdnjs 的对应公开版本，原文件头版权声明保留，许可证为 MIT。

已于 2026-10-22 核对参考仓库 JunhaoJian/junhaojian.github.io 的 main/LICENSE：MIT License，Copyright (c) 2026 JunhaoJian。完整许可原文保存在 site/licenses/reference-site-MIT.txt，并随站点分发。页面结构、主题定制、CSS 与导航脚本沿用参考站；双语内容、个人资料、语言切换和日期本地化已修改。本文件不代表原作者对本站的背书。原作者的个人内容不作为本人的经历发布。

已取得资源及 SHA-256 见 materials/reference/asset-manifest.json。

密码学习工具位于 lab/，使用 sm-crypto-v2 1.15.1（MIT）与锁定的 @noble 依赖，安装包中保留各自 LICENSE。来源、标准示例与核对边界见 lab/SOURCES.md，版本和完整性哈希见 lab/package-lock.json。它与静态个人网站分别运行，不随 site/ 发布。
