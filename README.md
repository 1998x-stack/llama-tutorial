# 🦙 LLaMA大模型技术 · 从入门到精通

> 📘 28章 实战体系 · 交互式 HTML 课程

> **English TL;DR:** An all-Chinese 28-chapter course on **Meta LLaMA large models** — walking through the architecture that defined the modern open Decoder-only LLM stack: RoPE, RMSNorm, SwiGLU, GQA, BPE/128K tiktoken vocab, scaling laws & training strategy, data engineering, 3D parallelism (LLaMA-1 2048-A100 → LLaMA-3 405B on 16K H100s), SFT & RLHF alignment, security/hallucination, quantization (GPTQ/AWQ/GGUF), context extension (NTK/YaRN), LoRA, deployment (vLLM/Ollama/llama.cpp), edge small models, and the LLaMA-4 MoE outlook.

## 📖 课程简介

本课程按 **Meta LLaMA 模型家族**的技术演进为主线，逐块拆解现代开源大模型的关键组件：从 Transformer 回顾、**RoPE / RMSNorm / SwiGLU / GQA** 四大架构基石，到 BPE 词表、缩放定律与训练策略、预训练数据工程，再到 LLaMA 1 的完整预训练流程（2048 A100 集群）、LLaMA 2 的 SFT / RLHF 对齐、LLaMA 3 的 405B 大规模训练系统（16K H100），以及量化、上下文扩展、LoRA 微调、部署、边缘小模型与 LLaMA 4 的 MoE 演进，形成从架构到训练到生产部署的完整闭环。

## 🎋 主线阶段

```
架构基石(RoPE/RMSNorm/SwiGLU/GQA) → 预训练(L1:2048卡) → 对齐(SFT/RLHF) → 规模化(L3:405B/16K卡) → 量化/扩展 → 部署/边缘 → 前沿(MoE)
```

## 🚀 快速开始

```bash
open index.html   # macOS，离线文件模式即可浏览全部章节
```

首页通过同目录的 `courses.js` 加载章节数据，不依赖在 `file://` 下可能被浏览器拦截的 `fetch('courses.json')`。请保持 `index.html`、`courses.js` 和各章 HTML 在相同相对路径下。

**维护课程目录时**，请只编辑 `courses.json`（唯一数据源），再生成并验证本地脚本数据：

```bash
python scripts/build_catalog.py --write
python scripts/build_catalog.py --check
python -m unittest discover -s tests -p 'test_*.py' -v
node tests/smoke-index.cjs  # 可选：需要 Node.js 18+
```

构建检查会校验章节数量、顺序、链接安全和 28 个页面文件的存在性，防止 `courses.js` 与 `courses.json` 不一致。无需安装第三方 Python 依赖。

## 📂 项目结构

```text
llama-tutorial/
├── index.html / 01.html ~ 28.html / courses.json / courses.js / theme.css
├── scripts/build_catalog.py
└── tests/
```

## 📖 章节目录

| # | 章节 | 核心 |
|---|---|------|
| 01–02 | LLaMA概述 + Transformer回顾 | Decoder-only 架构、三篇核心论文定位 |
| 03–06 | 架构基石 | RoPE、RMSNorm、SwiGLU、BPE/128K词表 |
| 07–10 | 缩放定律 + 数据 + 优化 | Chinchilla、预训练数据、AdamW/损失尖峰 |
| 11 | LLaMA 1 完整预训练 | 2048 A100 集群、3D 并行 |
| 12–14 | 对齐与安全 | SFT、RLHF/PPO、红队、幻觉抑制 |
| 15–16 | 量化与分布式 | GPTQ/AWQ/GGUF、3D/FSDP/ZeRO-3 |
| 17–18 | 上下文扩展 + 评估 | 8K→128K、NTK/YaRN、MMLU 方法论 |
| 19–20 | LLaMA 3 规模化 + 多模态 | 405B/16K H100、Vision |
| 21–24 | 能力增强 + 微调 | Function Calling、多语言、HF生态、LoRA/QLoRA |
| 25–28 | 部署 + 前沿 | vLLM/Ollama/llama.cpp、边缘小模型、LLaMA-4 MoE |

## 🎯 前置知识

- 适合：大模型研究者/工程师、开源 LLM 学习者
- 建议具备：Python + 基础深度学习；无需 GPU

## ✨ 特色

- 从架构基石到 405B 规模化 + MoE 前沿的完整演进线
- 聚焦三大开源 Baseline：TransformerLens 风格逐块拆解 + 生产部署 + 前沿趋势
- 即开即用纯静态 HTML

---
*本课程由 `llama-tutorial/` 项目维护。*