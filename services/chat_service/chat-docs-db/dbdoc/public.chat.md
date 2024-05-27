# public.chat

## Description

## Columns

| Name | Type | Default | Nullable | Children | Parents | Comment |
| ---- | ---- | ------- | -------- | -------- | ------- | ------- |
| user_id_1 | uuid |  | false |  |  |  |
| user_id_2 | uuid |  | false |  |  |  |
| id | uuid |  | false | [public.chat_message](public.chat_message.md) |  |  |
| created_at | timestamp with time zone |  | false |  |  |  |

## Constraints

| Name | Type | Definition |
| ---- | ---- | ---------- |
| chat_pkey | PRIMARY KEY | PRIMARY KEY (id) |

## Indexes

| Name | Definition |
| ---- | ---------- |
| chat_pkey | CREATE UNIQUE INDEX chat_pkey ON public.chat USING btree (id) |

## Relations

![er](public.chat.svg)

---

> Generated by [tbls](https://github.com/k1LoW/tbls)