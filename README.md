# Onto-X Project

## Introduction
The Onto-X Project aims to build a logical representation of a domain ontology that preserves both direct and indirect ancestor relationships among entities, enabling the reconstruction of hierarchical structures and the retrieval of all ancestor relationships for a given entity, along with their respective depths.

## Dataset
The dataset, `onto_x.csv`, is located in the `data` directory (`data/onto_x.csv`). It contains entities representing a hierarchy of pathologies, each described by:
- **Class Id**: A unique identifier for the entity within the ontology.
- **Preferred Label**: A human-readable name for the entity.
- **Parents**: One or more direct ancestors of the entity, separated by a `|`.

---

## Work Done

### Main Task

#### Principles and Code Explanation

The core goal of the code is to load the ontology from `onto_x.csv` into an internal graph-based data structure, allowing the extraction of hierarchical relationships. The script uses:

1. **Representation the Ontology as a Graph (Adjacency Lists)**  
   A graph is a natural choice for representing hierarchical or parent-child relationships. Each entity can be thought of as a "node" in the graph, and its links to parent entities can be represented as "edges" pointing upward in the hierarchy. By using a graph structure, we can:
   - **Easily traverse upwards or downwards:** Graphs make it straightforward to explore relationships in different directions. In our case, we often need to go upwards to find all ancestors.
   - **Handle multiple inheritance:** Some entities might have multiple parents, and a graph lets us represent these branching structures seamlessly.
   - **Enhance scalability:** As we add more entities, a graph-based approach continues to work efficiently and logically.

   In this code, we represent the graph as a **dictionary of lists** (an adjacency list). Each key is an entity’s unique Class ID, and the associated value is a list of its parent Class IDs. This format is memory-efficient and makes it simple to iterate over parents.

2. **Use of Breadth-First Search (BFS) for Ancestor Retrieval**  
   Once we have our graph in place, we need a method to find all the ancestors of a given entity and also determine how deep each ancestor is in the hierarchy. We use **Breadth-First Search (BFS)** for this task. BFS is a standard graph traversal algorithm that starts from a given node (in this case, the queried entity) and explores all of its immediate parents first (these are at depth 1), then all of the parents’ parents (depth 2), and so forth.

   **Why BFS?** BFS proceeds level by level:
   - It first finds all direct parents before moving on to grandparents and so forth. This naturally aligns with our idea of "depth."
   - It ensures that the shortest path to any ancestor (in terms of number of steps) is found first. For hierarchies, this makes it easy to calculate depths without additional logic.

   **Impact of BFS:**  
   By using BFS, the process of discovering ancestors and their depths is conceptually simple, efficient, and easy to understand. We know that the first time we encounter an ancestor, the depth recorded is the minimal possible—perfect for our use case.

---

**Functions:**

1. **`load_ontology(csv_path)`**  
   This function’s job is to read `onto_x.csv` and build three main data structures:
   - `id_to_label`: A dictionary that maps from each entity’s Class ID to its human-readable Preferred Label.
   - `label_to_id`: A dictionary that maps from the lowercase version of each Preferred Label back to its Class ID.
   - `graph`: A dictionary where each key is a Class ID, and each value is a list of that entity’s parent Class IDs.
   
   **Why we do this:**  
   - By separating IDs and labels, we give ourselves flexible querying options.
   - By building the `graph`, we prepare a structure ideal for fast traversal.

   *Example*: Suppose in the dataset we have:

| Class ID                                  | Preferred Label | Parents                                                                                                   |
|-------------------------------------------|-----------------|-----------------------------------------------------------------------------------------------------------|
| http://entity/CST/EXOPHTHALMOS            | EXOPHTHALMOS    | http://entity/CST/SS/EYE/GEN \| http://entity/CST/OPHLOCAL \| http://entity/CST/ENDOTHYR                 |

 After `load_ontology` runs:
- `id_to_label["http://entity/CST/EXOPHTHALMOS"]` will give "EXOPHTHALMOS".
- `label_to_id["EXOPHTHALMOS"]` will give "http://entity/CST/EXOPHTHALMOS".
- `graph["http://entity/CST/EXOPHTHALMOS"]` will be `["http://entity/CST/SS/EYE/GEN", "http://entity/CST/OPHLOCAL", "http://entity/CST/ENDOTHYR"]`.

With this, whenever we need to explore the ancestry of EXOPHTHALMOS, we know exactly which nodes to visit next: its parents.

2. **`get_ancestors_with_depth(class_id, graph, id_to_label)`**  
This function performs the BFS traversal to find all ancestors and record their depth. Starting from `class_id`, it moves up level by level. At the first level, it finds all direct parents (depth = 1). At the next level, it finds grandparents (depth = 2), and so forth.

**Why BFS here:**  
BFS ensures that when we first encounter an ancestor, we already know it’s at the shortest possible depth. There’s no need for complex checks or sorting; BFS naturally delivers the ancestors in order of increasing depth.

**Example:**  
Let’s say we query an entity "ACUTE BRAIN SYNDROME" (we can convert its label to a Class ID first). We run BFS up the graph:
- First, we find its direct parents, say "COGNITIVE/CORTICAL DISORDERS" , "BRAIN IRRITATION and ""PSYCHOSIS" .We assign them depth 1.
- Next, from each of those parents, we find their parents. Suppose "Nervous System" is two levels above. That means "Nervous System" is depth 2.

The function then returns a dictionary like:
```json
{
    "COGNITIVE/CORTICAL DISORDERS": 1,
    "BRAIN IRRITATION": 1,
    "PSYCHOSIS": 1,
    "Nervous System": 2
}
```
3. **`main()` function**:  
    The main function orchestrates the workflow:
    - Parses arguments (`--csv` for the CSV path and `--query` for the entity).
    - Loads the ontology using `load_ontology`.
    - Determines if the query is a Class ID or a Preferred Label and resolves it to a Class ID.
    - Calls `get_ancestors_with_depth` to retrieve ancestors and prints them in a structured format.

    
#### Decision and Approach Justification
- **Graph-based Representation**: Using a graph (in this case, a directed acyclic graph for hierarchies) is ideal for ontologies. It supports fast traversal and is a natural model for parent-child relationships.
- **Complexity**: BFS on this graph is efficient for retrieving ancestor paths, typically O(V + E) where V is the number of entities and E is the number of parent links. This is suitable for hierarchical data where each node can have multiple parents.

#### Recommendations for Future Work
- **Visualization**: Implementing a graph visualization tool could enable a user to explore the hierarchy visually, zoom in and out of specific branches, and gain insights into the ontology’s structure.

#### Installation Requirements
You can install the required dependencies with:
```bash
pip install -r requirements.txt
```
#### Running the Code

Execute the script by providing the CSV file path and a query term (Preferred Label):
You can install the required dependencies with:

```bash
python onto_x.py --csv <path_to_your_csv_file> --query <Class_ID_or_Label>
```
Real use example:

```bash
python onto_x.py --csv data/onto_x.csv --query "ACUTE BRAIN SYNDROME" or python onto_x.py --csv data/onto_x.csv --query "http://entity/CST/BRAIN%20SYND%20ACUTE"
```

#### Output Example

The script outputs a dictionary structure showing ancestors and their depths. For the query above:

```
{
    "COGNITIVE/CORTICAL DISORDERS": 1,
    "BRAIN IRRITATION": 1,
    "PSYCHOSIS": 1,
    "Nervous System": 2
}
```

### FastAPI

#### 1. Overview
The Onto-X Project includes a FastAPI application that provides an interactive interface for exploring and querying the ontology. By running this service, you can access:
- A browser-based interface (`index.html`) that allows you to search for entities and retrieve their ancestors.
- A set of HTTP endpoints that return ontology data in dictionary format, integrationg it with the front-end applications.

#### 2. Endpoints and Functionality

**GET `/`**
Returns the main HTML page, which includes a search box with autocomplete functionality. Users can type entity labels to fetch their ancestor information.

---

**GET `/ancestors`**
Given an entity (by label or Class ID), returns all its ancestors and their depths.  
- Depth 1 corresponds to direct parents.
- Depth 2 corresponds to grandparents, and so forth.

**Example Query:**
```http
GET /ancestors?query=EXOPHTHALMOS
```

---

### **GET `/search`**
Performs search for labels .  Used also for autocomplete suggestions.



---

## 3. Running the Application

### **1. Start the Server**
Launch the FastAPI application using Uvicorn:
```bash
uvicorn app.main:app --reload
```
By default, the server will run at `http://localhost:8000`.

---

### **2. Access the Application**
Visit `http://localhost:8000` to use the browser-based interface.

## 4. Screenshot of the Application

![Screenshot of FastAPI Interface](screenshots\fast_api_screenshot.png)


### Docker

#### Overview
The Onto-X project leverages Docker to provide a portable and consistent environment for deploying the FastAPI application. Using Docker ensures that the application runs reliably regardless of the underlying system configuration.

#### Dockerfile Explanation
The `Dockerfile` included in this project defines how the Docker image is built and what is included in the container:

- **Base Image**: The image is built on top of `python:3.12.3`, which provides a lightweight Python environment.
- **Working Directory**: The application files are placed in the `/app` directory within the container.
- **Files Copied**: 
  - The ontology data file (`data/onto_x.csv`) is included.
  - The `app` directory contains the FastAPI application code.
  - `requirements.txt` lists the Python dependencies.
- **Dependency Installation**: Python dependencies are installed using `pip`.
- **Port Exposure**: Port `8000` is exposed for accessing the FastAPI application.
- **Startup Command**: The container runs the FastAPI server using `uvicorn` when launched.

#### Building the Docker Image
To build the Docker image, use the following command in the project root directory (where the `Dockerfile` is located):
```bash
docker build -t ontox-api:latest .
```

#### Running the Docker Container
To run the Docker container, execute:
```bash
docker run -p 8000:8000 ontox-api:latest
```

This command maps the container's port `8000` to the host's port `8000`. Once the container is running, the application can be accessed at [http://localhost:8000](http://localhost:8000).