from notion_client import Client
import notiontaskr.config as config


client = Client(
    auth=config.NOTION_TOKEN,
)
filter = {
    "and": [
        {"property": "予定フラグ", "checkbox": {"equals": False}},
        {
            "and": [
                {
                    "property": "開始前通知時刻",
                    "formula": {"date": {"on_or_after": "2025-06-02T10:18:29.003Z"}},
                },
                {
                    "property": "開始前通知時刻",
                    "formula": {"date": {"on_or_before": "2025-06-02T10:49:29.003Z"}},
                },
            ]
        },
    ]
}
response_data = client.databases.query(
    **{
        "database_id": config.TASK_DB_ID,
        "filter": filter,
    }
)

print(response_data)
print()
