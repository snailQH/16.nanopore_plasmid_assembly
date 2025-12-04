import gzip
import argparse
from collections import Counter
import numpy as np
import os

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

def main():
    parser = argparse.ArgumentParser(description="Calculate read length distribution from a fastq file.")
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
        print(f"  Standard deviation: {np.std(lengths):.2f}")

        # Detailed length distribution
        counts = Counter(lengths)
        
        output_dir = args.output_dir if args.output_dir else os.path.dirname(fastq_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        base_filename = os.path.basename(fastq_file)
        output_file = os.path.join(output_dir, f"{base_filename}.length_dist.txt")


        print(f"\nSaving detailed length distribution to {output_file}")
        with open(output_file, 'w') as f:
            f.write("Length\tCount\n")
            for length, count in sorted(counts.items()):
                f.write(f"{length}\t{count}\n")
        
        print("-" * 30)

if __name__ == "__main__":
    main() 