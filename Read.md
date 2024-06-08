# Timestep Data Extraction and Molecule Processing

This repository contains a Python script for extracting timestep data from a simulation dump file and processing molecule data based on atom coordinates. The script performs the following tasks:

1. **Extract Timestep Data**: Reads a simulation dump file and extracts data for specified timesteps.
2. **Filter Lines**: Filters atom data lines to identify clusters of atoms within a specified distance.
3. **Process Molecule Data**: Analyzes molecule data to count the occurrence of different atom types and writes the results to an output file.

## Files

- `extract_timestep_data.py`: Python script containing the code with detailed comments.
- `README.md`: Documentation file.

## Usage

1. Place your simulation dump file (`nve300K.dump`) in the same directory as the script.
2. Run the script using a Python interpreter.
3. The script will create an `output_directory` (if it doesn't already exist) and generate output files for each timestep.

### Example

To extract data from timestep 470 to 500 from the input file `nve300K.dump` and save the results in `output_directory`:

```python
extract_timestep_data('nve300K.dump', 'output_directory', start_timestep=470, end_timestep=500, timestep_limit=470)
