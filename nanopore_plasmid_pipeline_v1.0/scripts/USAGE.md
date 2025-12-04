# 📖 使用说明

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install reportlab matplotlib numpy beautifulsoup4 --user
```

### 2. 生成单个样品HTML报告

```bash
cd scripts
python3 extract_sample_reports.py
```

**输出位置：** `../results/individual_reports/`

### 3. 生成AmpSeq品牌PDF报告

```bash
cd scripts
python3 generate_ampseq_reports.py
```

**输出位置：** `../results/ampseq_reports/`

## 📋 脚本详细说明

### extract_sample_reports.py

从合并的HTML报告中提取每个样品的独立报告。

**默认行为：**
- 输入：`../output/wf-clone-validation-report.html`
- 数据目录：`../output/`
- 输出：`../results/individual_reports/`

**使用示例：**
```bash
# 使用默认路径
python3 extract_sample_reports.py

# 自定义路径
python3 extract_sample_reports.py -i /path/to/report.html -o /path/to/output -d /path/to/data

# 只处理特定样品
python3 extract_sample_reports.py --samples UPA42701 USX140562

# 详细日志
python3 extract_sample_reports.py --verbose
```

### generate_ampseq_reports.py

生成AmpSeq品牌的PDF报告，参考 `001_N1_report.pdf` 格式。

**报告包含：**

1. **基本信息统计表**
   - Total DNA (Reads, Bases)
   - Host Genomic DNA (Reads, Bases)

2. **组装状态表**
   - 每个contig的详细信息：
     * Contig名称
     * 长度 (bp)
     * Reads Mapped
     * Bases Mapped
     * Multimer (%)
     * Coverage (x)
     * Is Circular

3. **Coverage Plots**
   - 每个contig一个coverage plot
   - 显示低置信度位置标记说明

4. **Read Length Distribution**
   - 使用 `get_length_dist_from_fastq.py` 生成
   - 显示读长分布图

**默认行为：**
- 数据目录：`../output/`
- 输出：`../results/ampseq_reports/`
- 自动从fastq文件统计Reads和Bases

**使用示例：**
```bash
# 使用默认路径
python3 generate_ampseq_reports.py

# 自定义路径
python3 generate_ampseq_reports.py -d /path/to/data -o /path/to/output

# 只处理特定样品
python3 generate_ampseq_reports.py --samples UPA42701 USX140562

# 详细日志
python3 generate_ampseq_reports.py --verbose
```

### generate_pdfs.sh

将HTML报告转换为PDF（备选方案）。

```bash
./generate_pdfs.sh [HTML_DIR] [OUTPUT_DIR]
```

**默认：**
- 输入：`../results/individual_reports/`
- 输出：`../results/individual_reports/`

## 📁 目录结构

```
project_root/
├── scripts/              # 所有脚本
│   ├── extract_sample_reports.py
│   ├── generate_ampseq_reports.py
│   ├── generate_pdfs.sh
│   ├── get_length_dist_from_fastq.py
│   └── README.md
├── output/               # 输入数据
│   ├── *.final.fasta
│   ├── *.final.fastq
│   ├── *.assembly_stats.tsv
│   ├── sample_status.txt
│   ├── plannotate.json
│   └── wf-clone-validation-report.html
└── results/              # 输出目录
    ├── individual_reports/    # HTML/PDF报告
    └── ampseq_reports/        # AmpSeq品牌PDF报告
```

## ⚙️ 路径说明

所有脚本都从 `scripts/` 目录运行，使用相对路径：

- **数据目录**：`../output/`（自动识别）
- **输出目录**：`../results/`（自动创建）

如需自定义，使用命令行参数：
```bash
python3 generate_ampseq_reports.py -d /absolute/path/to/data -o /absolute/path/to/output
```

## 🔍 故障排除

### 问题：找不到输入文件

```bash
# 检查数据目录
ls -la ../output/

# 使用绝对路径
python3 extract_sample_reports.py -i /absolute/path/to/report.html
```

### 问题：reportlab未安装

```bash
pip3 install reportlab matplotlib numpy beautifulsoup4 --user
```

### 问题：无法生成coverage plot

- Coverage plot使用模拟数据（placeholder）
- 实际使用时需要从alignment文件提取coverage数据

### 问题：无法生成read length分布图

- 确保 `get_length_dist_from_fastq.py` 在scripts目录
- 检查fastq文件是否存在
- 查看详细日志：`python3 generate_ampseq_reports.py --verbose`

## 📞 支持

如有问题，请访问：www.ampseq.com
