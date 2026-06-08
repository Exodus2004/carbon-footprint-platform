"""BigQuery service module streaming carbon footprint data asynchronously."""

import os
import logging
from datetime import datetime
from typing import Dict, Union, List, Optional
import anyio
from google.cloud import bigquery

logger: logging.Logger = logging.getLogger(__name__)

# Define the BigQuery schema for streaming insert
BQ_SCHEMA: List[bigquery.SchemaField] = [
    bigquery.SchemaField(
        "user_id",
        "STRING",
        mode="REQUIRED",
        description="Unique identifier for the user",
    ),
    bigquery.SchemaField(
        "timestamp",
        "TIMESTAMP",
        mode="REQUIRED",
        description="Time of the metrics submission",
    ),
    bigquery.SchemaField(
        "transportation_miles", "FLOAT", mode="REQUIRED", description="Miles traveled"
    ),
    bigquery.SchemaField(
        "energy_kwh", "FLOAT", mode="REQUIRED", description="Energy consumption in kWh"
    ),
    bigquery.SchemaField(
        "diet_meat_meals",
        "INTEGER",
        mode="REQUIRED",
        description="Number of meat meals",
    ),
]


async def stream_carbon_data(user_id: str, metrics: Dict[str, Union[int, float]]) -> None:
    """Streams carbon metric data into BigQuery asynchronously.

    Mocks the insertion if credentials are not fully configured.
    """
    dataset_id: str = os.getenv("BQ_DATASET_ID", "carbon_footprint_db")
    table_id: str = os.getenv("BQ_TABLE_ID", "user_metrics")
    project_id: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")

    row_to_insert: Dict[str, Union[str, float]] = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "transportation_miles": float(metrics.get("transportation_miles", 0.0)),
        "energy_kwh": float(metrics.get("energy_kwh", 0.0)),
        "diet_meat_meals": float(metrics.get("diet_meat_meals", 0.0)),
    }

    if not project_id:
        logger.info(
            f"[MOCK BIGQUERY INSERT] Would stream to {dataset_id}.{table_id}: {row_to_insert}"
        )
        return

    def perform_insert() -> Optional[List[Dict[str, Union[str, float]]]]:
        client: bigquery.Client = bigquery.Client()
        table_ref = client.dataset(dataset_id).table(table_id)
        errors = client.insert_rows_json(table_ref, [row_to_insert])
        if errors:
            return [dict(e) for e in errors]
        return None

    try:
        errors = await anyio.to_thread.run_sync(perform_insert)
        if errors:
            logger.error(f"Encountered errors while inserting rows: {errors}")
        else:
            logger.info("Successfully streamed carbon data to BigQuery.")
    except Exception as e:
        logger.error(f"BigQuery streaming failed: {e}")
