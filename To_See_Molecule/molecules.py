import os
import math

# User-dependent variables
input_file = 'nve300K.dump'     # Path to your input file
output_dir = 'output_directory' # Directory to store the extracted files
start_timestep = 300            # The starting timestep to extract
end_timestep = 500              # The ending timestep to extract
timestep_limit = 10000          # The maximum number of timesteps to process
distance_criterion = 1.7        # Distance criterion for filtering atoms
num_header_lines = 9            # Number of header lines in the input file
num_of_atoms = 5230             # Number of atoms
lines_per_timestep = num_of_atoms + num_header_lines    # Number of lines per timestep

def calculate_distance(coord1, coord2):
    """
    Calculate the Euclidean distance between two 3D coordinates.

    Parameters:
    - coord1: Tuple representing the first coordinate (x, y, z).
    - coord2: Tuple representing the second coordinate (x, y, z).

    Returns:
    - The Euclidean distance between the two coordinates.
    """
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(coord1, coord2)))

def filter_and_update_lines(input_lines):
    """
    Filter lines from the input data based on atom type and distance criteria and update the first element of each line.

    Parameters:
    - input_lines: List of lines from the input dump file.

    Returns:
    - A list of filtered and updated lines.
    """
    atoms = []
    lines_to_keep = []
    header_lines = input_lines[:num_header_lines]  # Store the header lines
    data_lines = input_lines[num_header_lines:]  # Data lines after the header

    # Collect atoms of types N and C
    for line in data_lines:
        parts = line.split()
        atom_type = parts[2]
        x, y, z = float(parts[3]), float(parts[4]), float(parts[5])
        if atom_type in {"N", "C"}:
            atoms.append((atom_type, x, y, z, line))
            lines_to_keep.append(line)
    
    # Include atoms of types O and H within a specified distance from N or C atoms
    for line in data_lines:
        parts = line.split()
        atom_type = parts[2]
        if atom_type in {"O", "H"}:
            x, y, z = float(parts[3]), float(parts[4]), float(parts[5])
            for _, nx, ny, nz, _ in atoms:
                distance = calculate_distance((x, y, z), (nx, ny, nz))
                if distance < distance_criterion:
                    lines_to_keep.append(line)
                    break

    # Update the first element of each data line
    for i, line in enumerate(lines_to_keep):
        parts = line.split()
        parts[0] = str(i + 1)
        lines_to_keep[i] = ' '.join(parts) + '\n'

    # Update the fourth line of the header with the number of lines changed
    header_lines[3] = f"{len(lines_to_keep)}\n"

    return header_lines + lines_to_keep

def extract_and_process_timesteps(input_file, output_dir, start_timestep, end_timestep, timestep_limit):
    """
    Extract specific timesteps data from the input file, filter and update them, and save to the output directory.

    Parameters:
    - input_file: Path to the input dump file.
    - output_dir: Directory where the processed timestep files will be saved.
    - start_timestep: The starting timestep to extract.
    - end_timestep: The ending timestep to extract.
    - timestep_limit: The maximum number of timesteps to process.
    """
    timestep_count = 0
    start_lines = []
    step_numbers = []

    # Read all lines from the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    # Identify the lines corresponding to the desired timesteps
    for i, line in enumerate(lines):
        if "ITEM: TIMESTEP" in line:
            timestep_count += 1
            if start_timestep <= timestep_count <= end_timestep:
                start_lines.append(i)
                step_numbers.append(lines[i + 1].strip())
            if timestep_count > timestep_limit:
                break

    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process and save the data for each identified timestep
    for start_line, step_number in zip(start_lines, step_numbers):
        end_line = start_line + lines_per_timestep  # Adjust this based on the number of atoms in your file
        timestep_lines = lines[start_line:end_line]
        processed_lines = filter_and_update_lines(timestep_lines)
        output_file = os.path.join(output_dir, f"modified_{step_number}.dump")

        with open(output_file, 'w') as out_file:
            out_file.writelines(processed_lines)

        print(f"Data from timestep {step_number} processed and written to {output_file}")

def merge_updated_files(output_dir, merged_output_file):
    """
    Merge all updated files in the output directory into a single output file.

    Parameters:
    - output_dir: Directory containing the updated files.
    - merged_output_file: Path to the merged output file.
    """
    merged_lines = []

    # Iterate through each updated file and collect their lines
    for file_name in sorted(os.listdir(output_dir)):
        if file_name.startswith("modified_") and file_name.endswith(".dump"):
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, 'r') as file:
                lines = file.readlines()
                merged_lines.extend(lines)

    # Write all collected lines to the merged output file
    with open(merged_output_file, 'w') as merged_file:
        merged_file.writelines(merged_lines)

    print(f"All updated dump files have been merged into {merged_output_file}")

# Usage
extract_and_process_timesteps(input_file, output_dir, start_timestep, end_timestep, timestep_limit)

# Merge the processed files into a single output file
merged_output_file = 'merged_output.dump'
merge_updated_files(output_dir, merged_output_file)
