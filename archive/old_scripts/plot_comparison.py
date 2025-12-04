import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os
import numpy as np

def plot_comparison(file_before, file_after, output_dir):
    """
    Reads two length distribution files and creates a comparative density plot.
    """
    try:
        # Read the data
        data_before = pd.read_csv(file_before, sep='\t')
        data_after = pd.read_csv(file_after, sep='\t')

        # Unpack the data for plotting
        lengths_before = np.repeat(data_before['Length'], data_before['Count'])
        lengths_after = np.repeat(data_after['Length'], data_after['Count'])
        
        # Create the plot
        plt.figure(figsize=(15, 7))
        
        # Plot both distributions
        sns.kdeplot(lengths_before, fill=True, label='Before Cleaning', color='salmon')
        sns.kdeplot(lengths_after, fill=True, label='After Cleaning', color='lightgreen')
        
        plt.title('Read Length Distribution: Before vs. After Cleaning')
        plt.xlabel('Read Length (bp)')
        plt.ylabel('Density')
        plt.grid(axis='both', alpha=0.5)
        
        # Use a log scale for the x-axis to better visualize the range of lengths
        plt.xscale('log')
        plt.legend()

        # Save the plot
        output_filename = os.path.join(output_dir, "read_length_comparison.png")
        plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Comparison plot saved to {output_filename}")

    except Exception as e:
        print(f"Could not create comparison plot. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Create a comparative density plot for two read length distributions.")
    parser.add_argument("file_before", help="Path to the .length_dist.txt file (before cleaning).")
    parser.add_argument("file_after", help="Path to the .length_dist.txt file (after cleaning).")
    parser.add_argument("--output-dir", default='.', help="Directory to save the output plot. Defaults to the current directory.")
    
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    plot_comparison(args.file_before, args.file_after, args.output_dir)

if __name__ == "__main__":
    main() 