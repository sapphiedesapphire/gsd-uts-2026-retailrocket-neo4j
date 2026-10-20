# UTS Graph Data Science: RetailRocket Recommendation with Neo4j

**Name:** Syafira Najema Putri Anisa | **NIM:** 24031554013 | **Course:** Graf Sains Data, UNESA

## Overview
Graph-based recommendation on the RetailRocket e-commerce dataset (Kaggle, Roman Zykov).
Visitors and items are stored in Neo4j; user similarity (cosine) and KNN (k = 5) are used to recommend items.

## Periods
| Fold | Dates | Rows |
|---|---|---|
| P1 (training) | 23/06/2015 to 01/07/2015 | 183,590 |
| P2 (testing) | 02/07/2015 to 10/07/2015 | 193,961 |

## Files
| File | Purpose |
|---|---|
| `retailrocket.ipynb` | Main notebook: wrangling, EDA, VSM, similarity, KNN, evaluation |
| `filter_periods.py` | Filters `events.csv` by timestamp into P1 and P2 |
| `import_retailrocket.py` | Imports a CSV into Neo4j in batches |
| `requirements.txt` | Python packages |
| `data/events_p1.csv`, `data/events_p2.csv` | Filtered datasets |
| `before_similarity.png`, `after_similarity.png` | Neo4j Browser screenshots (before and after similarity) |

## How to run
1. Create and activate a virtual environment, then `pip install -r requirements.txt`.
2. Download `events.csv` from [RetailRocket on Kaggle](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) into `data/`.
3. `python filter_periods.py` (recreates the P1 and P2 files).
4. Start a Neo4j instance, then `python import_retailrocket.py -p YOUR_PASSWORD -f events_p1.csv`.
5. Open `retailrocket.ipynb` and set the connection `URI` and `AUTH` in the first cells.

## Graph model
`(:Visitor)-[:VIEWED | :ADDED_TO_CART | :BOUGHT]->(:Item)` and `(:Visitor)-[:SIMILAR_TO {score}]->(:Visitor)`.

## Main results
- Subgraph: 98,513 visitors, 60,107 items, 183,590 interaction relationships.
- User matrix 98,513 x 60,107 and item matrix 60,107 x 98,513, both 99.9976% sparse.
- User-User projection chosen: 75.4% of users have at least one neighbour (items: 50.9%).
- Evaluation (random user 101175, seed 42): Hit@5 = 0, NDCG@5 = 0. Over 35 eligible users: Hit@5 = 0.0000, NDCG@5 = 0.0000.
