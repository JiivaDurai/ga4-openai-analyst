# Define the JSON schema for the functions
tools = [{
    "type": "function",
    "function": 
        {
        "name": "execute_sql_query",
        "description": "Execute an SQL query on BigQuery and return the results.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query to execute."
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        }
    }},
         {
    "type": "function",
    "function": 
    {
        "name": "get_table_schema",
        "description": "Fetch the schema of a specified table from BigQuery.",
        "parameters": {
            "type": "object",
            "properties": {
                "dataset": {
                    "type": "string",
                    "description": "The name of the dataset containing the table."
                },
                "table_name": {
                    "type": "string",
                    "description": "The name of the table to fetch the schema for."
                }
            },
            "required": ["dataset", "table_name"],
            "additionalProperties": False,
        }
    }
         }
]