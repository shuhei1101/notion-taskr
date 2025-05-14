# NotionTaskr

## 1. 目次
- [1. 目次](#1-目次)
- [2. 用語](#2-用語)
- [3. 概要](#3-概要)
- [4. GCP構成イメージ](#4-gcp構成イメージ)
- [5. 開発について](#5-開発について)
  - [5.1. 開発環境の構築](#51-開発環境の構築)
  - [5.2. ラベル追加回収時の対応方法](#52-ラベル追加回収時の対応方法)

## 2. 用語

| 用語                       | 説明                                                      |
| -------------------------- | --------------------------------------------------------- |
| 名前ラベル or ネームラベル | Notionのページタイトルに付与するラベル。[key-value]形式。 |


## 3. 概要
本システムはNotionデータベースと統合するために設計されたタスク管理システムである。


## 4. GCP構成イメージ
![GCP構成イメージ](docs/img/アプリ構成イメージ.png)
- 本ツールは、GCPのCloud Runの`Service`と`Job`を使用して、Notion APIを操作するAPIサーバーを構築する。
  - Cloud Runの`Service`とは、APIリクエストを受けてから、コンテナが起動し、処理を実行するサービス
  - Cloud Runの`Job`とは、処理を定期実行するサービス 
- バージョン管理は、GitHubを使用
- GitGub Actionsを使用して、CDを実現
  - mainブランチにpushされたら、GCPのCloud Runにデプロイする

## 5. 開発について

### 5.1. 開発環境の構築

1. 拡張機能をインストール
   - [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
2. `notion-api/docker-compose-yml`を開く
3. `Run Service`を選択
4. 左のタブ`Docker` > `Containers` > `notion-api`の折りたたみを開く
5. `notion-api`を右クリック > `Attach Shell`もしくは`Visual Studio Codeをアタッチする`を選択

### 5.2. ラベル追加回収時の対応方法
1. ○○Labelクラスを追加する
2. NameLabelクラスの`parse_labels`メソッドのhandlersに1.で追加したクラスを追加する
3. TaskNameクラスの`__eq__`メソッドにラベルの比較処理を追加する

