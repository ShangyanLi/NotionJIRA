# NotionJIRA
Add an auto-incrementing ticket id to your Notion tickets, JIRA-style. 
The workaround is dedicating a separate property to record the ticket number.

Before                     |  After
:-------------------------:|:-------------------------:
<img src="https://user-images.githubusercontent.com/9939724/124348512-257a7f00-db9f-11eb-942e-e136b033f121.png">  |  <img src="https://user-images.githubusercontent.com/9939724/124348514-28756f80-db9f-11eb-8ac9-6cfe6e931f66.png">


## Prereqs
1. Have the following ready (simply follow Steps 1 & 2 of the Notion's [Getting started guide](https://developers.notion.com/docs/getting-started#getting-started)): 
   1. your **Notion integration token**
   2. the **ID** of your Notion database
2. Inside your Notion database, add a ticket ID property whose type is **Number**, and make sure it's visible on your Kanban board view. You can use whatever name you prefer. The example here uses "Ticket ID."

<p align="center">
  <img src="https://user-images.githubusercontent.com/9939724/124348670-19db8800-dba0-11eb-8dd4-ed368230c2d3.png" width="30%">
</p>


## Setup
Simply copy the env example to a new `.env` file.
```shell
cp example.env .env
```
Replace its content with your own. Note that `NOTION_ID_PROP`'s value should be the name of the property you just created.

## Run
Run it with your favorite script scheduler.
