import os
import math

# User-Dependent Parameters
input_file = 'nve300K.dump'  # Path to your input file
merged_output_file = 'merged_output.dump'  # Path to the merged output file
start_timestep = 400  # The starting timestep to extract
end_timestep = 500  # The ending timestep to extract
timestep_limit = 10000  # The maximum number of timesteps to process
distance_criteria = 2.5  # The distance criterion for filtering atoms
header_lines_count = 9  # The number of header lines
atom_lines_count = 4970  # The number of atom data lines

# Derived Parameters
total_lines_per_timestep = header_lines_count + atom_lines_count

def extract_timestep_data():
    """
    Extract specific timesteps data from the input file.

    Returns:
    - A dictionary with timestep numbers as keys and their corresponding data lines as values.
    """
    timestep_count = 0
    timestep_data = {}
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    i = 0
    while i < len(lines):
        if "ITEM: TIMESTEP" in lines[i]:
            timestep_count += 1
            if start_timestep <= timestep_count <= end_timestep:
                timestep_number = lines[i + 1].strip()
                start_line = i
                end_line = i + total_lines_per_timestep + header_lines_count
                timestep_data[timestep_number] = lines[start_line:end_line]
            if timestep_count > timestep_limit:
                break
        i += 1
    return timestep_data

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

def filter_lines(data_lines):
    """
    Filter lines based on atom type and distance criteria.

    Parameters:
    - data_lines: List of data lines to be filtered.

    Returns:
    - A list of filtered lines.
    """
    atoms = []
    lines_to_keep = []

    for line in data_lines:
        parts = line.split()
        atom_type = parts[2]
        x, y, z = float(parts[3]), float(parts[4]), float(parts[5])
        if atom_type in {"N", "C"}:
            atoms.append((atom_type, x, y, z, line))
            lines_to_keep.append(line)
    
    for line in data_lines:
        parts = line.split()
        atom_type = parts[2]
        if atom_type in {"O", "H"}:
            x, y, z = float(parts[3]), float(parts[4]), float(parts[5])
            for _, nx, ny, nz, _ in atoms:
                distance = calculate_distance((x, y, z), (nx, ny, nz))
                if distance < distance_criteria:
                    lines_to_keep.append(line)
                    break

    return lines_to_keep

def update_first_element(data_lines):
    """
    Update the first element (index) of each data line.

    Parameters:
    - data_lines: List of data lines to be updated.

    Returns:
    - The updated list of data lines and the number of lines changed.
    """
    lines_changed = min(len(data_lines), atom_lines_count)  # Adjust based on the number of atoms in your file
    for i in range(lines_changed):
        parts = data_lines[i].split()
        parts[0] = str(i + 1)
        data_lines[i] = ' '.join(parts) + '\n'

    return data_lines, lines_changed

def process_and_merge():
    """
    Process the input file to extract, filter, and update timestep data, then merge the results into a single output file.
    """
    merged_lines = []
    
    timestep_data = extract_timestep_data()
    
    for timestep, data in timestep_data.items():
        header_lines = data[:header_lines_count]
        data_lines = data[header_lines_count:]
        
        filtered_lines = filter_lines(data_lines)
        updated_lines, lines_changed = update_first_element(filtered_lines)
        
        header_lines[3] = f"{lines_changed}\n"
        merged_lines.extend(header_lines + updated_lines)
    
    with open(merged_output_file, 'w') as file:
        file.writelines(merged_lines)
    
    print(f"All processed timestep data has been merged into {merged_output_file}")

# Run the process
process_and_merge()
