import csv
from collections import defaultdict, deque
from typing import Dict, List, Tuple

def load_ontology(csv_path: str):
    """
    Load the ontology data from a CSV file into graph structures.
    
    This function reads the CSV file containing ontology information and constructs three key data structures:
    - id_to_label: Maps each class ID to its preferred label.
    - label_to_id: Maps each preferred label (in lowercase) to its corresponding class ID for quick lookup.
    - graph: Represents the ontology as a directed graph where each class ID maps to a list of its parent class IDs.
    
    Args:
        csv_path (str): The file path to the CSV file containing the ontology data.
        
    Returns:
        Tuple[Dict[str, str], Dict[str, str], Dict[str, List[str]]]:
            - id_to_label: Dictionary mapping class IDs to preferred labels.
            - label_to_id: Dictionary mapping lowercase preferred labels to class IDs.
            - graph: Dictionary representing the ontology graph with class IDs as keys and lists of parent IDs as values.
    """
    id_to_label = {}
    label_to_id = {}
    graph = defaultdict(list)

    # Open and read the CSV file
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            class_id = row['Class ID'].strip()
            label = row['Preferred Label'].strip()
            parents = row['Parents'].strip() if row['Parents'] else ''

            # Populate the mappings from class ID to label and vice versa
            id_to_label[class_id] = label
            label_to_id[label.lower()] = class_id  # Use lowercase 

            # Build the graph by splitting the 'Parents' field by '|'
            if parents:
                parent_list = [p.strip() for p in parents.split('|')]
                graph[class_id].extend(parent_list)
            else:
                # If no parents are specified, assign an empty list
                graph[class_id] = []

    return id_to_label, label_to_id, dict(graph)


def get_ancestors_with_depth(class_id: str, graph: Dict[str, List[str]], id_to_label: Dict[str, str]) -> Dict[str, int]:
    """
    Retrieve all ancestors of a given class ID along with their depths in the ontology hierarchy.
    
    This function performs a breadth-first search (BFS) starting from the specified class ID to find all ancestor classes.
    Each ancestor is associated with a depth value indicating its distance from the starting class:
    - Depth 1: Direct parent
    - Depth 2: Grandparent
    - And so on...
    
    The special class "http://www.w3.org/2002/07/owl#Thing" is excluded from the results.
    
    Args:
        class_id (str): The class ID for which to find ancestors.
        graph (Dict[str, List[str]]): The ontology graph structure mapping class IDs to their parent IDs.
        id_to_label (Dict[str, str]): A mapping from class IDs to their preferred labels.
        
    Returns:
        Dict[str, int]: A dictionary where keys are the preferred labels of ancestor classes and values are their depths relative to the input class_id.
                        Returns an empty dictionary if no ancestors are found (excluding "owl#Thing").
    """
    relationships = {}  # To store ancestor labels and their depths
    queue = deque([(class_id, 0)])  # Queue for BFS, storing tuples of (current_class_id, current_depth)
    visited = set([class_id])  # To keep track of visited nodes and prevent cycles

    while queue:
        current_id, current_depth = queue.popleft()
        for parent_id in graph.get(current_id, []):
            # Skip the special class "owl#Thing" considered as no parent
            if parent_id == "http://www.w3.org/2002/07/owl#Thing":
                continue

            if parent_id not in visited:
                visited.add(parent_id)
                if parent_id in id_to_label:
                    # Record the ancestor's label and its depth
                    relationships[id_to_label[parent_id]] = current_depth + 1
                # Add the parent to the queue with incremented depth for further traversal
                queue.append((parent_id, current_depth + 1))

    return relationships


def find_entity_id(query: str, id_to_label: Dict[str, str], label_to_id: Dict[str, str]) -> str:
    """
    Determine if the query is a Class ID or a Preferred Label and return the corresponding Class ID.
    
    This function first checks if the query matches any existing Class ID. If not, it attempts a case-insensitive
    match against the preferred labels to find the corresponding Class ID.
    
    Args:
        query (str): The query string, which can be either a Class ID or a Preferred Label.
        id_to_label (Dict[str, str]): A mapping from class IDs to their preferred labels.
        label_to_id (Dict[str, str]): A mapping from lowercase preferred labels to class IDs.
        
    Returns:
        str: The Class ID corresponding to the query if found; otherwise, returns None.
    """
    query = query.strip()
    # Check if the query is a Class ID
    if query in id_to_label:
        return query
    # Attempt to match the query as a Preferred Label
    q_lower = query.lower()
    if q_lower in label_to_id:
        return label_to_id[q_lower]
    # If no match is found, return None
    return None
