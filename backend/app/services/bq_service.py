from google.cloud import bigquery
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Define the BigQuery schema for streaming insert
BQ_SCHEMA = [
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED", description="Unique identifier for the user"),
    bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED", description="Time of the metrics submission"),
    bigquery.SchemaField("transportation_miles", "FLOAT", mode="REQUIRED", description="Miles traveled"),
    bigquery.SchemaField("energy_kwh", "FLOAT", mode="REQUIRED", description="Energy consumption in kWh"),
    bigquery.SchemaField("diet_meat_meals", "INTEGER", mode="REQUIRED", description="Number of meat meals"),
]

def stream_carbon_data(user_id: str, metrics: dict):
    """
    Streams carbon metric data into BigQuery.
    Mocks the insertion if credentials are not fully configured.
    """
    dataset_id = os.getenv("BQ_DATASET_ID", "carbon_footprint_db")
    table_id = os.getenv("BQ_TABLE_ID", "user_metrics")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    row_to_insert = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "transportation_miles": metrics.get("transportation_miles", 0),
        "energy_kwh": metrics.get("energy_kwh", 0),
        "diet_meat_meals": metrics.get("diet_meat_meals", 0)
    }

    if not project_id:
        logger.info(f"[MOCK BIGQUERY INSERT] Would stream to {dataset_id}.{table_id}: {row_to_insert}")
        return

    try:
        client = bigquery.Client()
        table_ref = client.dataset(dataset_id).table(table_id)
        
        # Verify table exists or let BQ create/fail based on config
        # In a real environment, you'd ensure the table exists with the BQ_SCHEMA
        
        errors = client.insert_rows_json(table_ref, [row_to_insert])
        if errors:
            logger.error(f"Encountered errors while inserting rows: {errors}")
        else:
            logger.info("Successfully streamed carbon data to BigQuery.")
    except Exception as e:
        logger.error(f"BigQuery streaming failed: {e}")
