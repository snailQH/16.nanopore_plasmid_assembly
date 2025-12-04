# AmpSeq 质粒报告生成工具

## 📋 项目目录结构

```
wf-clone-validation_3721d4d6-1e08-4db4-861c-f373b6934c07/
├── scripts/              # 所有脚本文件
│   ├── extract_sample_reports.py       # 提取单个样品HTML报告
│   ├── generate_ampseq_reports.py      # 生成AmpSeq品牌PDF报告
│   ├── generate_pdfs.sh                # HTML转PDF工具
│   └── get_length_dist_from_fastq.py   # Read长度分布图生成
├── output/               # 输入数据目录
│   ├── *.final.fasta
│   ├── *.final.fastq
│   ├── *.assembly_stats.tsv
│   ├── sample_status.txt
│   ├── plannotate.json
│   └── wf-clone-validation-report.html
└── results/              # 输出目录
    ├── individual_reports/    # 单个样品HTML/PDF报告
    └── ampseq_reports/        # AmpSeq品牌PDF报告
```

## 🔧 安装依赖

### Python 依赖

```bash
pip3 install reportlab matplotlib numpy beautifulsoup4 --user
```

### 系统依赖

- Google Chrome (用于HTML转PDF)

## 📝 脚本说明

### 1. extract_sample_reports.py

从合并的HTML报告中提取每个样品的独立报告。

```bash
# 基本用法（从scripts目录运行）
cd scripts
python3 extract_sample_reports.py

# 指定输入输出
python3 extract_sample_reports.py -i ../output/wf-clone-validation-report.html -o ../results/my_reports

# 只处理特定样品
python3 extract_sample_reports.py --samples UPA42701 USX140562
```

**输出位置：** `../results/individual_reports/`

### 2. generate_ampseq_reports.py

生成AmpSeq品牌的PDF报告，包含：
- 基本信息统计（Reads, Bases）
- 组装状态和contig信息
- Coverage plots
- Read length分布图

```bash
# 基本用法
cd scripts
python3 generate_ampseq_reports.py

# 指定数据目录和输出目录
python3 generate_ampseq_reports.py -d ../output -o ../results/ampseq_reports

# 只处理特定样品
python3 generate_ampseq_reports.py --samples UPA42701 USX140562
```

**输出位置：** `../results/ampseq_reports/`

### 3. generate_pdfs.sh

将HTML报告转换为PDF格式。

```bash
# 基本用法
cd scripts
./generate_pdfs.sh

# 指定输入和输出目录
./generate_pdfs.sh ../results/individual_reports ../results/individual_reports
```

### 4. get_length_dist_from_fastq.py

生成read长度分布图（PDF和PNG格式）。

```bash
# 基本用法
python3 get_length_dist_from_fastq.py sample.fastq

# 批量处理
python3 get_length_dist_from_fastq.py *.final.fastq --output-dir ../results/length_dist
```

## 🎯 使用流程

### 生成单个样品HTML报告

```bash
cd scripts
python3 extract_sample_reports.py
```

### 生成AmpSeq品牌PDF报告

```bash
cd scripts
python3 generate_ampseq_reports.py
```

### 将HTML转换为PDF（备选方案）

```bash
cd scripts
./generate_pdfs.sh
```

## 📊 报告内容

### extract_sample_reports.py 生成的报告包含：
- Sample status（仅当前样品）
- Plannotate 注释结果
- Read Counts 统计
- Read stats 质量图表
- Dot plots 比对图

### generate_ampseq_reports.py 生成的报告包含：
- 基本信息统计表（Total DNA, Host Genomic DNA）
- 组装状态表（每个contig的详细信息）
- 每个contig的Coverage plot
- Read length分布图
- AmpSeq公司信息（页眉页脚）

## ⚙️ 默认路径

所有脚本都使用相对路径，默认：

- **数据目录**：`../output/`
- **输出目录**：`../results/`
  - `individual_reports/` - HTML和PDF报告
  - `ampseq_reports/` - AmpSeq品牌PDF报告

## 📝 注意事项

1. 确保所有依赖已安装
2. 确保数据文件在`output/`目录中
3. 脚本会自动创建输出目录
4. 从`scripts/`目录运行脚本时，会使用相对路径自动定位数据

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
pip3 install reportlab --user
```

### 问题：无法生成PDF

- 检查Chrome是否正确安装
- 检查HTML文件是否存在
- 查看详细日志：添加`-v`或`--verbose`参数

## 📞 支持

如有问题，请访问：www.ampseq.com

