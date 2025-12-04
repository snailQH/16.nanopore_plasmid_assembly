#!/usr/bin/env python3
import gzip
import argparse
from collections import Counter
import numpy as np
import os
import matplotlib.pyplot as plt

def get_read_lengths(fastq_file):
    """
    Reads a fastq file (gzipped or not) and returns a list of read lengths.
    """
    lengths = []
    open_func = gzip.open if fastq_file.endswith('.gz') else open
    with open_func(fastq_file, 'rt') as f:
        for i, line in enumerate(f):
            if i % 4 == 1:
                lengths.append(len(line.strip()))
    return lengths


def plot_length_distribution(lengths, output_prefix):
    """
    Generate a histogram plot (PDF + PNG) of read lengths.
    """
    plt.figure(figsize=(8, 5))
    bins = np.linspace(0, max(lengths), 100)
    plt.hist(lengths, bins=bins, color="#4C72B0", edgecolor="black", alpha=0.75)

    plt.xlabel("Read Length", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title("Read Length Distribution", fontsize=14, fontweight="bold")

    median_len = np.median(lengths)
    plt.axvline(median_len, color="red", linestyle="--", linewidth=1.5)
    plt.text(median_len * 1.02, plt.ylim()[1] * 0.9,
             f"apparent length: {int(median_len)}",
             color="red", fontsize=10, va="top")

    plt.tight_layout()

    # Save figures
    pdf_file = f"{output_prefix}.pdf"
    png_file = f"{output_prefix}.png"
    plt.savefig(pdf_file)
    plt.savefig(png_file, dpi=300)
    plt.close()
    print(f"[OK] Saved plots: {pdf_file}, {png_file}")


def main():
    parser = argparse.ArgumentParser(description="Calculate read length distribution from a fastq file and plot histogram.")
    parser.add_argument("fastq_files", nargs='+', help="Path to one or more fastq files (can be gzipped).")
    parser.add_argument("--output-dir", help="Directory to save output files. Defaults to the directory of the input file.")
    
    args = parser.parse_args()

    for fastq_file in args.fastq_files:
        print(f"Processing {fastq_file}...")
        try:
            lengths = get_read_lengths(fastq_file)
        except FileNotFoundError:
            print(f"Error: File not found: {fastq_file}")
            continue
        except Exception as e:
            print(f"An error occurred while processing {fastq_file}: {e}")
            continue
            
        if not lengths:
            print(f"No reads found in {fastq_file}")
            continue

        # Basic stats
        print("\nStatistics:")
        print(f"  Total reads: {len(lengths)}")
        print(f"  Min length: {np.min(lengths)}")
        print(f"  Max length: {np.max(lengths)}")
        print(f"  Mean length: {np.mean(lengths):.2f}")
        print(f"  Median length: {np.median(lengths)}")
        print(f"  Std deviation: {np.std(lengths):.2f}")

        # Length distribution counts
        counts = Counter(lengths)
        output_dir = args.output_dir if args.output_dir else os.path.dirname(fastq_file)
        os.makedirs(output_dir, exist_ok=True)
            
        base_filename = os.path.basename(fastq_file)
        output_txt = os.path.join(output_dir, f"{base_filename}.length_dist.txt")
        output_prefix = os.path.join(output_dir, f"{base_filename}.length_dist")

        print(f"Saving detailed length distribution to {output_txt}")
        with open(output_txt, 'w') as f:
            f.write("Length\tCount\n")
            for length, count in sorted(counts.items()):
                f.write(f"{length}\t{count}\n")

        # Generate plot
        plot_length_distribution(lengths, output_prefix)
        print("-" * 50)


if __name__ == "__main__":
    main()
