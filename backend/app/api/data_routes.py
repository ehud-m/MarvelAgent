from fastapi import APIRouter
from app.api.models import BuildDatasetRequest, BuildDatasetResponse
from app.data.build_dataset import build_marvel_dataframe
from app.data.ingest_to_neo4j import ingest_to_neo4j

router = APIRouter(prefix="/data")

marvel_df = None
superpower_gene_mapping = None

@router.post("/build", response_model=BuildDatasetResponse)
async def build_data_route():
    global marvel_df
    global superpower_gene_mapping
    marvel_df, superpower_gene_mapping = build_marvel_dataframe()

    if marvel_df is None:
        return BuildDatasetResponse(number_of_characters=0)

    return BuildDatasetResponse(number_of_characters=len(marvel_df))


@router.post("/ingest")
async def ingest_data_route(request: BuildDatasetRequest):
    global marvel_df
    global superpower_gene_mapping
    if marvel_df is None:
        return {"status": "Data not built yet."}

    marvel_df_to_ingest = marvel_df.head(request.number_of_characters)
    ingest_to_neo4j(marvel_df_to_ingest, superpower_gene_mapping)
    return {"status": f"Ingested {len(marvel_df_to_ingest)} characters"}
