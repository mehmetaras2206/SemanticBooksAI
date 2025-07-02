import pandas as pd
from sentence_transformers import SentenceTransformer

# 1. MiniLM-Modell laden
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. CSV einlesen
df = pd.read_csv("books.csv", encoding="utf-8")

# 3. Kombinierte Texte vorbereiten: Titel + Beschreibung
combined_texts = (df["title"].fillna("") + ". " + df["description"].fillna("")).tolist()

# 4. Embeddings berechnen
embeddings = model.encode(combined_texts, show_progress_bar=True)

# 5. Optional: Embeddings als neue Spalte speichern
df["embedding"] = [vec.tolist() for vec in embeddings]

# 6. Ergebnis speichern (wenn gewünscht)
df.to_csv("books_embeddings.csv", index=False, encoding="utf-8")

print("✅ Embeddings erfolgreich erzeugt.")
