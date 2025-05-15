# notiontaskr仕様書

## 目次
- [目次](#目次)
- [概要](#概要)
- [GCP構成イメージ](#gcp構成イメージ)
- [Taskドメイン - クラス図](#taskドメイン---クラス図)

## 概要
- NotionのDBとNotionAPIを使用して、タスクの予実管理を行うシステム

## GCP構成イメージ

```mermaid
graph TD
  GitHub --> |mainブランチへのpush| GitHubActions
  GitHubActions --> |デプロイ| GCP[Google Cloud Platform]
  
  subgraph GCP
    CloudRunService[Cloud Run Service] --> |APIリクエスト処理| NotionAPI
    CloudRunRegularJob[Cloud Run Regular Job] --> |定期的な同期処理| NotionAPI
    CloudRunDailyJob[Cloud Run Daily Job] --> |日次の完全同期| NotionAPI
    
    NotionAPI --> NotionDB[Notion Database]
    
    CloudStorage[Cloud Storage] <--> |キャッシュの保存/取得| Services[Cloud Run Service/Jobs]
  end
```
- アプリ本体はGCPのCloud Run上で動作(サービス/ジョブ)
- Cloud Runには1m間隔とデイリーで定期実行するJobがある
  - 1m間隔: 1m前までのタスクを取得し、変更があれば関連するタスクを更新
  - デイリー: 過去1年分のタスクを取得し、キャッシュ(pickle)に変換し、GCSに保存
- Cloud Runのサービスは現在使用していない。
- GCPの構成は以下図を参照してください。

## Taskドメイン - クラス図
```mermaid
classDiagram
  class Task {  
    +PageId page_id  
    +TaskName name  
    +List~Tag~ tags  
    +NotionId id  
    +Status status  
    +PageId parent_task_page_id  
    +bool is_updated  
    +update_name()  
    +update_status()  
    +update_parent_task_page_id()  
  }  
    
  class ScheduledTask {  
    +ManHours scheduled_man_hours  
    +ManHours executed_man_hours  
    +List~ExecutedTask~ executed_tasks  
    +List~ScheduledTask~ sub_tasks  
    +ProgressRate progress_rate  
    +update_executed_tasks_properties()  
    +update_sub_tasks_properties()  
    +update_status_to_check_properties()  
    +calc_progress_rate()  
    +aggregate_man_hours()  
  }  
    
  class ExecutedTask {  
    +PageId scheduled_task_page_id  
    +Date date  
    +ManHours man_hours  
  }  
    
  Task <|-- ScheduledTask  
  Task <|-- ExecutedTask  
  ScheduledTask "1" o-- "many" ExecutedTask : executed_tasks  
  ScheduledTask "1" o-- "many" ScheduledTask : sub_tasks  

```
- Notion DBから取得したデータは、主に`予定タスク`と`実績タスク`に分けられる
  - `予定タスク`: タスクの予定を示すデータ。予定タスクは内部に実績タスクのリストを持つ。
  - `実績タスク`: タスクの実績を示すデータ。
- タスクは、親タスクと子タスクの関係を持つことができる。
- タスクについての詳細は、以下のクラス図を参照してください。
  - ※クラスの内部構造は2025/5/15時点のものです。


