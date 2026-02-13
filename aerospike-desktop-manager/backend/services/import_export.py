"""Data import/export service."""

import csv
import io
import json

import aerospike_py


class ImportExportService:
    def __init__(self, client: aerospike_py.AsyncClient):
        self.client = client

    async def export_json(self, ns: str, set_name: str) -> str:
        """Export all records from a set as JSON."""
        records = await self.client.scan(ns, set_name)
        result = []
        for key, meta, bins in records:
            entry = {"key": key, "meta": meta, "bins": bins}
            result.append(entry)
        return json.dumps(result, default=str, indent=2)

    async def export_csv(self, ns: str, set_name: str) -> str:
        """Export all records from a set as CSV."""
        records = await self.client.scan(ns, set_name)
        if not records:
            return ""

        # Collect all bin names
        all_bins = set()
        for _, _, bins in records:
            if bins:
                all_bins.update(bins.keys())

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["_key", "_gen", "_ttl"] + sorted(all_bins))
        writer.writeheader()

        for key, meta, bins in records:
            row = {
                "_key": key[2] if key else "",
                "_gen": meta.get("gen", "") if meta else "",
                "_ttl": meta.get("ttl", "") if meta else "",
            }
            if bins:
                for k, v in bins.items():
                    row[k] = json.dumps(v) if isinstance(v, (dict, list)) else v
            writer.writerow(row)

        return output.getvalue()

    async def import_json(self, ns: str, set_name: str, data: str) -> int:
        """Import records from JSON data. Returns count of imported records."""
        records = json.loads(data)
        count = 0
        for entry in records:
            bins = entry.get("bins", {})
            key_val = entry.get("key")
            if key_val and isinstance(key_val, (list, tuple)) and len(key_val) >= 3:
                pk = key_val[2]
            elif "pk" in entry:
                pk = entry["pk"]
            else:
                continue
            key = (ns, set_name, pk)
            await self.client.put(key, bins)
            count += 1
        return count
