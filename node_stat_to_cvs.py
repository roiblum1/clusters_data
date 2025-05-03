import pandas as pd
import re
import os
import glob

def parse_node_data(file_path, cluster_name):
    """
    Parse node data from a text file and add cluster information
    """
    # Initialize lists to store data
    node_names = []
    server_models = []
    cpu_cores = []
    ram_sizes = []
    gpu_types = []
    clusters = []
    
    # Read the file
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Split the content into node blocks
        node_blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in node_blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            
            node_name = ""
            server_model = ""
            cpu_core = ""
            ram_size = ""
            gpu_type = ""
            
            for line in lines:
                line = line.strip()
                
                # Skip separator lines
                if line.startswith('----'):
                    continue
                    
                # Extract data based on line prefix
                if line.startswith('Node name:'):
                    node_name = line.replace('Node name:', '').strip()
                elif line.startswith('Server model:'):
                    server_model = line.replace('Server model:', '').strip()
                elif line.startswith('CPU cores:'):
                    cpu_core = line.replace('CPU cores:', '').strip()
                elif line.startswith('Total RAM:'):
                    ram_size = line.replace('Total RAM:', '').strip()
                elif line.startswith('GPU type:'):
                    gpu_type = line.replace('GPU type:', '').strip()
            
            # Only add the data if we found a node name
            if node_name:
                node_names.append(node_name)
                server_models.append(server_model)
                cpu_cores.append(cpu_core)
                ram_sizes.append(ram_size)
                gpu_types.append(gpu_type)
                clusters.append(cluster_name)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return pd.DataFrame()
    
    # Create a DataFrame
    df = pd.DataFrame({
        'Cluster': clusters,
        'Node Name': node_names,
        'Server Model': server_models,
        'CPU Cores': cpu_cores,
        'Total RAM': ram_sizes,
        'GPU Type': gpu_types
    })
    
    return df

def parse_cluster_data(file_path, cluster_name):
    """
    Parse cluster data from a cluster_info.txt file
    """
    cluster_info = {
        'Cluster Name': cluster_name,
        'Total Nodes': '',
        'Pods Available': '',
        'Nodes at Max Pods': ''
    }
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('Total nodes:'):
                cluster_info['Total Nodes'] = line.replace('Total nodes:', '').strip()
            elif line.startswith('Pods available:'):
                cluster_info['Pods Available'] = line.replace('Pods available:', '').strip()
            elif line.startswith('Node in max pods:'):
                cluster_info['Nodes at Max Pods'] = line.replace('Node in max pods:', '').strip()
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return cluster_info

def process_all_clusters(base_dir, node_output_file, cluster_output_file):
    """
    Process all nodes_info.txt and cluster_info.txt files across multiple cluster directories
    """
    # Find all cluster directories
    cluster_dirs = glob.glob(os.path.join(base_dir, "cluster*"))
    
    # Initialize empty DataFrames to store all data
    all_node_data = pd.DataFrame()
    all_cluster_data = []
    
    # Process each cluster directory
    for cluster_dir in cluster_dirs:
        cluster_name = os.path.basename(cluster_dir)
        nodes_info_path = os.path.join(cluster_dir, "nodes_info.txt")
        cluster_info_path = os.path.join(cluster_dir, "cluster_info.txt")
        
        # Process nodes_info.txt
        if os.path.exists(nodes_info_path):
            print(f"Processing {cluster_name} nodes: {nodes_info_path}")
            df = parse_node_data(nodes_info_path, cluster_name)
            all_node_data = pd.concat([all_node_data, df], ignore_index=True)
        else:
            print(f"Warning: No nodes_info.txt found in {cluster_dir}")
        
        # Process cluster_info.txt
        if os.path.exists(cluster_info_path):
            print(f"Processing {cluster_name} cluster info: {cluster_info_path}")
            cluster_info = parse_cluster_data(cluster_info_path, cluster_name)
            all_cluster_data.append(cluster_info)
        else:
            print(f"Warning: No cluster_info.txt found in {cluster_dir}")
    
    # Save node data to Excel
    if not all_node_data.empty:
        all_node_data.to_excel(node_output_file, index=False)
        print(f"\nNode inventory Excel file created: {node_output_file}")
        print(f"Total nodes processed: {len(all_node_data)}")
    else:
        print("No node data found to process")
    
    # Save cluster data to Excel
    if all_cluster_data:
        cluster_df = pd.DataFrame(all_cluster_data)
        cluster_df.to_excel(cluster_output_file, index=False)
        print(f"Cluster inventory Excel file created: {cluster_output_file}")
        print(f"Total clusters processed: {len(all_cluster_data)}")
    else:
        print("No cluster data found to process")
    
    return all_node_data, pd.DataFrame(all_cluster_data)

# Example usage
if __name__ == "__main__":
    base_directory = "cluster_info"  # Updated to match your directory name
    node_output_excel = "all_nodes_inventory.xlsx"
    cluster_output_excel = "all_clusters_inventory.xlsx"
    
    node_df, cluster_df = process_all_clusters(base_directory, node_output_excel, cluster_output_excel)
    print("\nPreview of node data:")
    print(node_df.head())
    print("\nPreview of cluster data:")
    print(cluster_df.head())