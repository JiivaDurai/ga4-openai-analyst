from google.cloud import bigquery

client = bigquery.Client(project="cl-test-project")

# Define the functions that can be called
def execute_sql_query(query: str) -> dict:
    try:
        query_job = client.query(query)
        result = query_job.result()
        rows = [dict(row) for row in result]
        return {"status": "success", "data": rows}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_table_schema(dataset: str, table_name: str) -> dict:
    try:
        table_ref = client.dataset(dataset).table(table_name)
        table = client.get_table(table_ref)
        schema = [{"name": field.name, "type": field.field_type} for field in table.schema]
        return schema
    except Exception as e:
        return {"status": "error", "error": str(e)}