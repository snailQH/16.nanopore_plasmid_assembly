# 📋 项目整理完成总结

## ✅ 完成的工作

### 1. 脚本整理
- ✅ 所有脚本已移动到 `scripts/` 目录
- ✅ 所有脚本已更新为使用相对路径
- ✅ 默认输出目录设置为 `results/`

### 2. 脚本列表

#### scripts/extract_sample_reports.py
- **功能**：从合并HTML报告提取单个样品报告
- **默认输出**：`../results/individual_reports/`
- **默认数据目录**：`../output/`

#### scripts/generate_ampseq_reports.py
- **功能**：生成AmpSeq品牌PDF报告（参考格式）
- **包含内容**：
  - 基本信息统计（Reads, Bases）
  - 组装状态表（每个contig）
  - Coverage plots（每个contig）
  - Read length分布图
- **默认输出**：`../results/ampseq_reports/`
- **默认数据目录**：`../output/`

#### scripts/generate_pdfs.sh
- **功能**：HTML转PDF工具
- **默认输入**：`../results/individual_reports/`
- **默认输出**：`../results/individual_reports/`

#### scripts/get_length_dist_from_fastq.py
- **功能**：生成read长度分布图
- **已集成到**：`generate_ampseq_reports.py`

### 3. 目录结构

```
wf-clone-validation_3721d4d6-1e08-4db4-861c-f373b6934c07/
├── scripts/              # ✅ 所有脚本
│   ├── extract_sample_reports.py
│   ├── generate_ampseq_reports.py
│   ├── generate_pdfs.sh
│   ├── get_length_dist_from_fastq.py
│   └── README.md
├── output/               # 输入数据（保持不变）
│   ├── *.final.fasta
│   ├── *.final.fastq
│   ├── sample_status.txt
│   ├── plannotate.json
│   └── wf-clone-validation-report.html
└── results/              # ✅ 输出目录（自动创建）
    ├── individual_reports/    # HTML/PDF报告
    └── ampseq_reports/        # AmpSeq品牌PDF报告
```

## 🚀 使用方法

### 生成单个样品HTML报告

```bash
cd scripts
python3 extract_sample_reports.py
```

输出到：`../results/individual_reports/`

### 生成AmpSeq品牌PDF报告

```bash
cd scripts
python3 generate_ampseq_reports.py
```

输出到：`../results/ampseq_reports/`

### HTML转PDF（备选方案）

```bash
cd scripts
./generate_pdfs.sh
```

## 📦 依赖安装

```bash
pip3 install reportlab matplotlib numpy beautifulsoup4 --user
```

## ⚙️ 路径说明

所有脚本使用相对路径，从 `scripts/` 目录运行时：
- 数据目录：`../output/`（自动识别）
- 输出目录：`../results/`（自动创建）

如需自定义路径，使用命令行参数：
```bash
python3 generate_ampseq_reports.py -d /path/to/data -o /path/to/output
```

