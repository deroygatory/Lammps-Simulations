import re
import sys

def parse_cfg_file(input_filename, output_filename=None):
    with open(input_filename, 'r') as file:
        lines = file.readlines()
    
    # Extract number of particles from the first line
    num_particles_line = lines[0].strip()
    match = re.match(r'Number of particles = (\d+)', num_particles_line)
    if not match:
        raise ValueError("The first line does not contain the number of particles in the expected format.")
    num_particles = int(match.group(1))
    
    atom_data = []
    header_lines = []
    id_index = None
    start_index = None

    # Separate header lines and find the index of 'id'
    for i, line in enumerate(lines):
        if re.match(r'^\d+\.\d+', line):
            start_index = i
            break
        header_lines.append(line)
        if line.startswith('auxiliary'):
            match = re.match(r'auxiliary\[(\d+)\] = id', line)
            if match:
                id_index = int(match.group(1)) + 4  # Convert to 1-based index

    if id_index is None:
        raise ValueError("No auxiliary line found with 'id'")

    # Extract atom data starting from the first mass line
    i = start_index
    while i < len(lines):
        if re.match(r'^\d+\.\d+', lines[i]):
            mass = lines[i].strip()
            atom_type = lines[i+1].strip()
            coords_id_line = lines[i+2].strip().split()
            id_value = coords_id_line[id_index - 1]  # Convert to 0-based index
            
            atom_data.append((id_value, mass, atom_type, coords_id_line))
            i += 3
        else:
            i += 1

    # Sort atom data by atom id
    atom_data.sort(key=lambda x: int(x[0]))

    # Default output filename if not provided
    if output_filename is None:
        output_filename = f"sorted_{input_filename}"

    # Write sorted data to a new file
    with open(output_filename, 'w') as file:
        # Write header lines
        file.writelines(header_lines)
        # Write sorted atom data
        for id_value, mass, atom_type, coords_id_line in atom_data:
            file.write(f"{mass}\n{atom_type}\n{' '.join(coords_id_line)}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cfgformating.py <input_filename> [output_filename]")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else None
    
    parse_cfg_file(input_filename, output_filename)
