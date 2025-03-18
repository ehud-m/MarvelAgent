import json

from fastapi import APIRouter
from app.api.models import ChatInput, ChatResponse
from app.core.agent_runner import run_cypher_agent
from app.db.neo4j_client import Neo4jClient
from app.db.redis_client import RedisClient
from app.api.data_routes import router as data_router


router = APIRouter()
router.include_router(data_router)

@router.post("/question", response_model=ChatResponse)
async def ask_question(chat_input: ChatInput):
    redis_key = chat_input.message.strip().lower()
    cached = RedisClient.get_instance().get(redis_key)
    if cached:
        return ChatResponse(message=cached)

    result = run_cypher_agent(chat_input.message, debug=True)
    if result['final_answer']:
        RedisClient.get_instance().set(redis_key, result['final_answer'])
    return ChatResponse(message=result['final_answer'])

@router.get("/graph/{character}")
async def get_character_neighbors(character: str):
    query = f"""
        MATCH (c:Character {{name: $characterName}})
        OPTIONAL MATCH (c)-[:MEMBER_OF]->(t:Team)
        OPTIONAL MATCH (c)-[hm:HAS_MUTATION]->(g:Gene)
        OPTIONAL MATCH (c)-[:POSSESSES_POWER]->(p1:Power)
        OPTIONAL MATCH (g)-[conf:CONFERS]->(p2:Power)
        
        WITH c, 
             collect(DISTINCT t.name) AS teams,
             collect(DISTINCT {{
               name: g.name,
               weight: hm.weight
             }}) AS genes,
             collect(DISTINCT CASE
               WHEN p1 IS NOT NULL THEN {{
                 name: p1.name,
                 source: 'direct'
               }}
               WHEN p2 IS NOT NULL THEN {{
                 name: p2.name,
                 source: 'from_gene',
                 gene: g.name,
                 weight: conf.weight
               }}
             END) AS powers
        
        RETURN {{
          character: c.name,
          description: c.description,
          teams: teams,
          genes: genes,
          powers: powers
        }} AS result
        """
    return json.dumps(Neo4jClient.get_instance().query_knowledge_graph(query, params={"characterName": character}))
