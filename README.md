
Agent autonome qui transforme une question en langage naturel en requête SQL, l'exécute sur une base SQLite locale et s'auto-corrige en cas d'erreur avant de renvoyer une réponse synthétique.

Orchestration LangGraph pour gérer la boucle de correction et modèle Phi3 (ollama).

---

## Principe

1. **Génération SQL** → Le LLM lit la question et le schéma, puis génère une requête SQL.
2. **Exécution** → La requête s'exécute sur SQLite. Si erreur (syntaxe, colonne inexistante), on capture le message d'erreur.
3. **Décision** → Si erreur ET tentatives < 3, on reboucle à l'étape 1 en injectant l'erreur au LLM pour qu'il la corrige.
4. **Réponse** → Sinon, on synthétise une réponse en langage naturel à partir des résultats.


![1788432626013](image/README/1788432626013.png)



## Architecture

Le projet est minimaliste et modulaire :

**src/**

- **state.py** → Définit `AgentState` (TypedDict) : question, schéma, requête SQL, erreur, résultats, compteur de tentatives, réponse finale.
- **llm.py** → Factory pour charger Ollama depuis `.env`.
- **db.py** → Connexion SQLite, extraction du schéma DDL, exécution des requêtes.
- **nodes.py** → Les 3 nœuds du graphe (generate_sql, execute_sql, format_answer) + la fonction de routage (should_continue).
- **graph.py** → Assemblage du StateGraph et compilation.

**À la racine**

- **main.py** → CLI interactive.
- **setup_db.py** → Génère la base de test `ecommerce.db`.

---

## Base de données

La base de test `ecommerce.db` contient 3 tables simples :

**users** : id, name, email, country, created_at
**products** : id, name, category, price, stock
**orders** : id, user_id, product_id, quantity, total_price, order_date, status

Le schéma est extrait **dynamiquement** depuis `sqlite_master`, donc vous pouvez brancher n'importe quelle base SQLite (chinook.db, etc.) en changeant `DB_PATH` dans `.env`.

Exemples de questions :

- "Combien de commandes ont été livrées ?"
- "Quel est le chiffre d'affaires total des commandes livrées ?"
- "Quels sont les top 3 produits par revenu ?"
- "Quel utilisateur a dépensé le plus ?"

---

## Modèle

**phi3** par défaut (3.8B, très rapide en CPU).

Pour changer de modèle, éditez `.env` :

```
LLM_MODEL=mistral
```

Puis téléchargez-le : `ollama pull mistral`

Autres modèles recommandés pour CPU :

- **phi3** (par défaut, ~8 GB RAM, ~5-10 sec)
- **tinyllama** (~2-3 GB RAM, très rapide mais moins capable)
- **mistral** (~16 GB RAM, meilleure qualité mais plus lent)

---

## Visualisation LangSmith 

Vous pouvez tracer chaque exécution du graphe sur **LangSmith** pour debugging .

Créez un compte gratuit : https://smith.langchain.com

`.env` :

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_...
LANGCHAIN_PROJECT=sql-agent
```


---

## Installation


```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```


```bash
ollama serve
```

```bash
ollama pull phi3
```

**Générer base de test**

```bash
python setup_db.py
```

**Lancer agent**

```bash
python main.py
```


Si le LLM génère une requête invalide, on voit l'auto-correction en action :

```
[generate_sql]
  SELECT SUM(amount) FROM orders WHERE status = 'livré';
[execute_sql]
  Échec: OperationalError: no such column: amount

[Correction #1] OperationalError: no such column: amount
  SELECT SUM(total_price) FROM orders WHERE status = 'livré';
[execute_sql]
  1 ligne(s)
[format_answer]

Le chiffre d'affaires total des commandes livrées est 1 436,88 €.
```
