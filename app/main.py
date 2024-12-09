from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pathlib import Path
import uvicorn

from app.onto_x import load_ontology, get_ancestors_with_depth, find_entity_id

# Define the path to the ontology CSV file relative to this script
DATA_PATH = Path(__file__).parent.parent / "data" / "onto_x.csv"

# Load the ontology data during the startup of the application
id_to_label, label_to_id, graph = load_ontology(str(DATA_PATH))

# Initialize the FastAPI application
app = FastAPI()

# Configure the template directory for rendering HTML templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

@app.get("/", response_class=JSONResponse)
def root(request: Request):
    """
    Root  that serves the index.html template.
    
    """
    return templates.TemplateResponse("index.html", {"request": request, "labels": list(id_to_label.values())})


@app.get("/ancestors")
def get_ancestors(query: str):
    """
    Retrieve all ancestors of a specified entity along with their depths.

    """
    # Determine the Class ID based on the query
    class_id = find_entity_id(query, id_to_label, label_to_id)
    if not class_id:
        # Raise a 404 error if the entity is not found
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Retrieve the ancestors and their depths
    ancestors = get_ancestors_with_depth(class_id, graph, id_to_label)
    
    # Prepare the output dictionary
    output = {}
    for label, depth in ancestors.items():
        output[label] = depth
    
    return output


@app.get("/search")
def search_labels(query: str):
    """
    Search for entity labels that match the query string + Autocomplete.

    """
    query_lower = query.lower()
    # Find all labels that contain the query substring (case-insensitive)
    matches = [label for label in id_to_label.values() if query_lower in label.lower()]
    return {"suggestions": matches}

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    To run the FastAPI server, execute the following command in your terminal:

    uvicorn app.main:app --reload
    """
