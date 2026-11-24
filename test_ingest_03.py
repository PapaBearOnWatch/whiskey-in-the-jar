from pathlib import Path
from collector.email_ingest import ingest_email

sample_path = Path("samples/test_email_03.eml")
raw_email = sample_path.read_bytes()

result = ingest_email(raw_email)

print("\nWHISKEY IN THE JAR - THIRD EMAIL COLLECTION")
print("=" * 50)

for key, value in result.items():
    print(f"{key}: {value}")
