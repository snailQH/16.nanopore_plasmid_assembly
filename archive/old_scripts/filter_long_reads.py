import gzip
import argparse
import os

def filter_long_reads(input_file, output_file, min_length):
    """
    Reads a gzipped FASTQ file, filters for long reads, and writes them to a new gzipped FASTQ file.
    """
    print(f"Processing {input_file}...")
    reads_written = 0
    total_reads = 0
    
    with gzip.open(input_file, 'rt') as f_in, gzip.open(output_file, 'wt') as f_out:
        while True:
            header = f_in.readline()
            if not header:
                break # End of file
            
            seq = f_in.readline()
            plus = f_in.readline()
            qual = f_in.readline()
            
            total_reads += 1
            
            if len(seq.strip()) > min_length:
                f_out.write(header)
                f_out.write(seq)
                f_out.write(plus)
                f_out.write(qual)
                reads_written += 1
    
    print(f"Finished processing {input_file}.")
    print(f"  Total reads found: {total_reads}")
    print(f"  Reads longer than {min_length} bp: {reads_written}")
    print(f"  Filtered reads saved to: {output_file}\n")


def main():
    parser = argparse.ArgumentParser(description="Filter long reads from gzipped FASTQ files.")
    parser.add_argument("fastq_files", nargs='+', help="Path to one or more gzipped FASTQ files.")
    parser.add_argument("--min-length", type=int, default=2000, help="Minimum read length to keep (default: 2000).")
    parser.add_argument("--output-dir", help="Directory to save output files. Defaults to the directory of the input file.")
    
    args = parser.parse_args()

    for fastq_file in args.fastq_files:
        try:
            output_dir = args.output_dir if args.output_dir else os.path.dirname(fastq_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            base_filename = os.path.basename(fastq_file)
            name_part = base_filename.replace('.fastq.gz', '').replace('.fq.gz', '')
            output_filename = os.path.join(output_dir, f"{name_part}_long.fastq.gz")
            
            filter_long_reads(fastq_file, output_filename, args.min_length)
            
        except FileNotFoundError:
            print(f"Error: File not found: {fastq_file}")
            continue
        except Exception as e:
            print(f"An error occurred while processing {fastq_file}: {e}")
            continue

if __name__ == "__main__":
    main() 