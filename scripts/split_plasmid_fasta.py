#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_plasmid_fasta.py
------------------------------------
Split plasmid FASTA sequences into fixed-length fragments.
Support specifying input/output/sample name through command-line arguments.

Usage:
    python split_plasmid_fasta.py --input INPUT.fasta --outdir OUTDIR [--sample SAMPLE] [--size 2000]

Example:
    python split_plasmid_fasta.py --input plasmid.fasta --outdir fragments --sample test01
"""

import os
import argparse
from Bio import SeqIO

DEFAULT_FRAGMENT_SIZE = 2000  # bp


def split_fasta(input_fasta, output_dir, sample_name=None, fragment_size=DEFAULT_FRAGMENT_SIZE):
    """Split each FASTA sequence into smaller fragments."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Ensure output directory is writable
    if not os.access(output_dir, os.W_OK):
        raise PermissionError(f"Output directory is not writable: {output_dir}")

    for record in SeqIO.parse(input_fasta, "fasta"):
        seq = record.seq
        seq_len = len(seq)

        for i in range(0, seq_len, fragment_size):
            fragment = seq[i:i + fragment_size]
            part_num = (i // fragment_size) + 1

            # output name supports sample name
            if sample_name:
                fragment_id = f"{sample_name}_{record.id}_part{part_num}"
            else:
                fragment_id = f"{record.id}_part{part_num}"

            output_path = os.path.join(output_dir, f"{fragment_id}.fasta")

            # Write fragment
            with open(output_path, "w") as out_f:
                out_f.write(">1.0\n")
                for j in range(0, len(fragment), 80):
                    out_f.write(str(fragment[j:j + 80]) + "\n")

            print(f"[OK] Wrote {output_path} ({len(fragment)} bp)")


def main():
    parser = argparse.ArgumentParser(description="Split plasmid FASTA into fixed-length fragments.")

    parser.add_argument("--input", "-i", required=True, help="Input FASTA file")
    parser.add_argument("--outdir", "-o", required=True, help="Output directory")
    parser.add_argument("--sample", "-s", default=None, help="Sample name prefix for output files")
    parser.add_argument("--size", "-l", type=int, default=DEFAULT_FRAGMENT_SIZE,
                        help="Fragment size (default: 2000 bp)")

    args = parser.parse_args()

    # Input validation
    if not os.path.isfile(args.input):
        raise FileNotFoundError(f"Input FASTA not found: {args.input}")

    split_fasta(
        input_fasta=args.input,
        output_dir=args.outdir,
        sample_name=args.sample,
        fragment_size=args.size,
    )

