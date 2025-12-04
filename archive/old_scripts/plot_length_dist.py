import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import numpy as np

def plot_length_distribution(file_path, output_dir):
    """
    Reads a length distribution file and creates a histogram plot.
    """
    try:
        # Read the data
        data = pd.read_csv(file_path, sep='\t')
        
        # Unpack the data for plotting
        lengths = np.repeat(data['Length'], data['Count'])

        # Create the plot
        plt.figure(figsize=(12, 6))
        
        # Determine appropriate bins
        max_len = lengths.max()
        # Use Freedman-Diaconis rule for bin width, but cap number of bins to avoid performance issues
        iqr = np.subtract(*np.percentile(lengths, [75, 25]))
        if iqr > 0:
            bin_width = 2 * iqr * (len(lengths) ** (-1/3))
            num_bins = int((max_len - lengths.min()) / bin_width) if bin_width > 0 else 50
            num_bins = min(num_bins, 500) # Cap number of bins
        else:
            num_bins = 50
            
        plt.hist(lengths, bins=num_bins, color='skyblue', edgecolor='black')
        
        plt.title(f'Read Length Distribution for {os.path.basename(file_path)}')
        plt.xlabel('Read Length (bp)')
        plt.ylabel('Frequency (Count)')
        plt.grid(axis='y', alpha=0.75)
        
        # Use a log scale for the y-axis to better visualize low-count lengths
        plt.yscale('log')
        plt.gca().set_ylim(bottom=0.8) # set bottom to avoid issues with log(0)

        # Add some summary statistics to the plot
        mean_len = lengths.mean()
        median_len = np.median(lengths)
        plt.axvline(mean_len, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean_len:.2f}')
        plt.axvline(median_len, color='g', linestyle='dashed', linewidth=2, label=f'Median: {median_len:.2f}')
        plt.legend()

        # Save the plot
        base_filename = os.path.basename(file_path)
        output_filename = os.path.join(output_dir, f"{base_filename}.png")
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Plot saved to {output_filename}")

    except Exception as e:
        print(f"Could not process {file_path}. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Plot read length distribution from a .length_dist.txt file.")
    parser.add_argument("dist_files", nargs='+', help="Path to one or more .length_dist.txt files.")
    parser.add_argument("--output-dir", default='.', help="Directory to save output plots. Defaults to the current directory.")
    
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for dist_file in args.dist_files:
        plot_length_distribution(dist_file, args.output_dir)

if __name__ == "__main__":
    main() 