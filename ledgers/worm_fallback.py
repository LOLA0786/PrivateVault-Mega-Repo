from datetime import datetime, timezone

UTC = timezone.utc


class WORMFallback:
    def __init__(self):
        self.records = []

    def write(self, data):
        self.records.append(
            {
                "timestamp": datetime.now(UTC),
                "data": data,
            }
        )

    def read_all(self):
        return self.records
