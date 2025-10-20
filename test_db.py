from backend.database.db_manager import db

# Get total posts
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM raw_posts')
total = cursor.fetchone()[0]
print(f"📊 Total posts in database: {total}")

cursor.execute('SELECT source, COUNT(*) as count FROM raw_posts GROUP BY source')
sources = cursor.fetchall()
print("\n📰 Posts by source:")
for source in sources:
    print(f"  - {source['source']}: {source['count']} posts")

cursor.execute('SELECT text, source, country FROM raw_posts LIMIT 5')
sample = cursor.fetchall()
print("\n📝 Sample posts:")
for i, post in enumerate(sample, 1):
    print(f"\n{i}. [{post['source']}] ({post['country']})")
    print(f"   {post['text'][:100]}...")

conn.close()