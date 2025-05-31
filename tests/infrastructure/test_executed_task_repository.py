from notion_client import Client
import notiontaskr.config as config


client = Client(
    auth=config.NOTION_TOKEN,
)
filter = {
    "property": "開始前通知時刻",
    "formula": {"date": {"after": "2025-05-31T15:40:00.000+09:00"}},
}
response_data = client.databases.query(
    **{
        "database_id": config.TASK_DB_ID,
        "filter": filter,
    }
)

print(response_data)
print()
