# MarvelAgent
This project implements an intelligent assistant built on a hybrid system that combines a **Neo4j knowledge graph**, a **large language model (LLM)**, and a **LangGraph-based agentic pipeline** to answer user queries about Marvel characters, their powers, genetic mutations, and team affiliations. The system includes both a **frontend (React)** and a **backend (FastAPI)** and uses **Redis** to cache responses and avoid redundant LLM calls. **LangGraph** orchestrates the backend agent workflow, enabling multi-step reasoning through query generation, validation, execution, summarization, and answer refinement.



## Features

- Structured Neo4j knowledge graph with entities: Characters, Genes, Powers, and Teams
- Graph-augmented LLM reasoning pipeline using LangGraph
- Supports Cypher query generation, validation, execution, summarization, and answer refinement
- API with endpoints for question answering, graph exploration, and data ingestion
- Dataset construction from a curated Marvel subset
- Redis-based query caching
- Frontend UI for interactive querying

---

## Requirements

- Python 3.10+
- Node.js (for the frontend)
- Redis
- Neo4j (local or remote)

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
cd frontend
npm install
```

### Environment Variables

Configure a `.env` file or set the following variables:

```env
OPENAI_API_KEY=your-openai-key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## Setup Instructions

### Run the Backend (FastAPI)

```bash
uvicorn app.main:app --reload
```

### Run the Frontend (React)

```bash
cd frontend
npm run dev
```

---

## API Endpoints

### POST `/question`

Accepts a natural language question from the user and returns a context-rich answer grounded in the knowledge graph.

**Request Body:**
```json
{
  "message": "What gene gives Wolverine his healing power?"
}
```

**Response:**
```json
{
  "message": "Wolverine’s healing factor is linked to Gene B, which has high confidence in enabling accelerated healing."
}
```

---

### GET `/graph/{character}`

Returns the immediate neighbors of a given character in the knowledge graph, including powers, gene mutations (with confidence weights), team affiliations, and a textual description.

**Example Request:**
```
GET /graph/Wolverine
```

**Example Response:**
```json
{
  "character": "Wolverine",
  "description": "...",
  "teams": ["X-Men"],
  "genes": [
    { "name": "Gene B", "weight": 0.94 }
  ],
  "powers": [
    { "name": "Accelerated Healing", "source": "direct" }
  ]
}
```

---

### POST `/data/build`

Constructs the Marvel dataset by filtering and transforming raw superhero data. Prepares the data for ingestion into the graph.

**Response:**
```json
{
  "number_of_characters": 1267
}
```

---

### POST `/data/ingest`

Ingests a specified number of characters from the prepared dataset into the Neo4j graph database.

**Request Body:**
```json
{
  "number_of_characters": 100
}
```

**Response:**
```json
{
  "status": "Ingested 100 characters"
}
```

---

## Usage Flow

1. Click **Build Dataset** in the frontend to prepare data.
2. Specify how many characters to ingest.
3. Ask questions such as:
   - “What gene gives Spider-Man his powers?”
   - “Which powers are granted by Gene A?”
   - “Who in the X-Men can teleport?”

---

## Graph Schema

### Entities

- `Character`: name, description
- `Team`: name
- `Gene`: name
- `Power`: name

### Relationships

- `(Character)-[:MEMBER_OF]->(Team)`
- `(Character)-[:HAS_MUTATION {weight}]->(Gene)`
- `(Gene)-[:CONFERS {weight}]->(Power)`
- `(Character)-[:POSSESSES_POWER]->(Power)`

### Example Cypher Query

```cypher
MATCH (c:Character)-[:HAS_MUTATION]->(g:Gene)
MATCH (g)-[:CONFERS]->(p:Power)
RETURN c.name, g.name, p.name
```

---


## LangGraph Pipeline (LLM Workflow)

Each natural language query is processed by a dynamic, multi-step agent built with LangGraph. The pipeline coordinates LLM-driven reasoning and graph-based querying through the following steps:

1. **Decision Node** – Determines the next required action based on the agent’s state (e.g., generate query, summarize, etc.)
2. **Query Generation** – Converts the user’s natural language question into a Cypher query using a prompt-tuned LLM.
3. **Query Validation** – The generated query is validated both semantically (using another LLM) and structurally (against the Neo4j schema using `EXPLAIN`).
4. **Query Execution** – Executes the Cypher query against the Neo4j knowledge graph and stores the raw result.
5. **Summarization** – If needed, character descriptions are summarized using an LLM to make the output more digestible.
6. **Answer Generation** – Uses the LLM to turn query results into clear, human-readable answers grounded in the graph data.
7. **Answer Judgment** – Evaluates the final answer’s clarity, completeness, and accuracy using a separate LLM step.
8. **Refinement Loop** – If the answer is poor or incomplete, the agent resets and regenerates the Cypher query.

### How the Knowledge Graph and LLM Are Combined

The agent first retrieves structured facts from the Neo4j knowledge graph using Cypher queries. These results—containing entities like characters, genes, powers, and relationships with weights—are then passed to the LLM using carefully designed prompts. The LLM is asked to interpret and explain the factual results from the graph. This separation between data retrieval (via the knowledge graph) and language generation (via the LLM) ensures both accuracy and fluency in the final answers.

---

## Notes

- Gene-to-power mappings are assigned heuristically using alphabetical gene labels (e.g., Gene A, Gene B, ...).
- Each `HAS_MUTATION` and `CONFERS` relationship includes a `weight` to simulate confidence or scientific uncertainty. These weights are incorporated into the final answers when relevant.
- Redis is used to cache previous user queries and responses, significantly reducing LLM usage for repeated questions.
- Each LLM node in the LangGraph pipeline uses a **custom-crafted system prompt** tailored to its role (e.g., query generation, validation, summarization).
- **Few-shot examples** are embedded into the prompts where appropriate, especially for query generation and validation, to ensure correct use of schema and Cypher syntax.
