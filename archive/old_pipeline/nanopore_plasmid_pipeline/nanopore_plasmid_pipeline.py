import os
import sys
import argparse
import logging
from datetime import datetime
import subprocess

def run_command(command, log_file, env_path):
    """Runs a command and logs its output, adding the conda env to the PATH."""
    logging.info(f"Executing command: {' '.join(command)}")
    
    # Get a copy of the current environment and prepend the conda env bin path
    env = os.environ.copy()
    env['PATH'] = os.path.join(env_path, 'bin') + os.pathsep + env['PATH']
    
    with open(log_file, 'a') as f:
        f.write(f"--- Executing: {' '.join(command)} ---\n")
        process = subprocess.run(command, stdout=f, stderr=subprocess.PIPE, text=True, env=env)
        if process.returncode != 0:
            error_message = f"Command failed with exit code {process.returncode}\n"
            if process.stderr:
                error_message += f"Stderr: {process.stderr}\n"
            logging.error(error_message)
            raise RuntimeError(error_message)
    logging.info("Command finished successfully.")


def main():
    """
    Main function to run the plasmid assembly pipeline.
    """
    # --- Configuration ---
    CONDA_ENV_PATH = "/data4/liqh/mambaforge/envs/pipeline_env_v2"
    
    parser = argparse.ArgumentParser(description="Nanopore Plasmid Assembly and Annotation Pipeline")
    parser.add_argument("-i", "--input_file", required=True, help="Path to the input FASTQ file.")
    parser.add_argument("-o", "--output_dir", required=True, help="Path to the output directory.")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use.")
    parser.add_argument("--medaka_model", default="r1041_e82_400bps_sup_v5.0.0", help="Medaka consensus model.")
    parser.add_argument("--genus", default="Escherichia", help="Genus for Prokka annotation.")
    parser.add_argument("--species", default="coli", help="Species for Prokka annotation.")
    parser.add_argument("--strain", default="K12", help="Strain for Prokka annotation.")
    parser.add_argument("--locustag", default="PROKKA", help="Locus tag for Prokka annotation.")

    args = parser.parse_args()

    # --- Logging Setup ---
    os.makedirs(args.output_dir, exist_ok=True)
    log_file_main = os.path.join(args.output_dir, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_file_main), logging.StreamHandler(sys.stdout)])

    # --- Dependency Check ---
    logging.info("Step 1: Checking for dependencies...")
    executables = {
        'flye': 'bin/flye', 'medaka_consensus': 'bin/medaka_consensus', 'samtools': 'bin/samtools',
        'minimap2': 'bin/minimap2', 'nanoplot': 'bin/NanoPlot', 'prokka': 'bin/prokka'
    }
    for name, rel_path in executables.items():
        path = os.path.join(CONDA_ENV_PATH, rel_path)
        if not os.path.exists(path):
            logging.error(f"Dependency not found: {path}. Please ensure the conda environment is set up correctly.")
            sys.exit(1)
        executables[name] = path # Update with full path
    
    logging.info("All dependencies found.")

    try:
        # --- Flye Assembly ---
        logging.info("Step 2: Running Flye assembler...")
        flye_dir = os.path.join(args.output_dir, 'flye_assembly')
        flye_log = os.path.join(args.output_dir, 'flye.log')
        flye_cmd = [
            executables['flye'], '--nano-raw', args.input_file, 
            '--out-dir', flye_dir, '--threads', str(args.threads)
        ]
        run_command(flye_cmd, flye_log, CONDA_ENV_PATH)
        assembly_file = os.path.join(flye_dir, 'assembly.fasta')

        # --- Medaka Polishing ---
        logging.info("Step 3: Running Medaka for polishing...")
        medaka_dir = os.path.join(args.output_dir, 'medaka_polished')
        medaka_log = os.path.join(args.output_dir, 'medaka.log')
        medaka_cmd = [
            executables['medaka_consensus'],
            '-d', assembly_file,       # Draft assembly
            '-i', args.input_file,      # Input reads
            '-o', medaka_dir,           # Output directory
            '-m', args.medaka_model,
            '-t', str(args.threads)
        ]
        run_command(medaka_cmd, medaka_log, CONDA_ENV_PATH)
        polished_assembly = os.path.join(medaka_dir, 'consensus.fasta')

        # --- Prokka Annotation (SKIPPED) ---
        logging.warning("Step 4: SKIPPING Prokka annotation due to persistent environment issues.")
        # logging.info("Step 4: Running Prokka for annotation...")
        # prokka_dir = os.path.join(args.output_dir, 'prokka_annotation')
        # prokka_log = os.path.join(args.output_dir, 'prokka.log')
        # prokka_cmd = [
        #     executables['prokka'], '--outdir', prokka_dir, '--prefix', 'plasmid',
        #     '--genus', args.genus, '--species', args.species, '--strain', args.strain,
        #     '--locustag', args.locustag, '--cpus', str(args.threads), '--force',
        #     polished_assembly
        # ]
        # run_command(prokka_cmd, prokka_log, CONDA_ENV_PATH)
        
        logging.info("Pipeline finished successfully (Annotation Skipped).")
        logging.info(f"Final polished assembly available at: {polished_assembly}")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 