import os
import json
import csv
from abc import ABC, abstractmethod
from typing import List, Dict, Any

REPORTS_DIR = "reports"

def _ensure_reports_dir() -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    return REPORTS_DIR

class ReportExportStrategy(ABC):
    @abstractmethod
    def export(self, data: List[Dict[str, Any]], filename: str) -> str:
        pass

class CsvExportStrategy(ReportExportStrategy):
    def export(self, data: List[Dict[str, Any]], filename: str) -> str:
        _ensure_reports_dir()
        filepath = os.path.join(REPORTS_DIR, f"{filename}.csv")
        if not data:
            return filepath
        fieldnames = list(data[0].keys())
        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return filepath

class JsonExportStrategy(ReportExportStrategy):
    def export(self, data: List[Dict[str, Any]], filename: str) -> str:
        _ensure_reports_dir()
        filepath = os.path.join(REPORTS_DIR, f"{filename}.json")
        with open(filepath, mode='w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return filepath

class TxtExportStrategy(ReportExportStrategy):
    def export(self, data: List[Dict[str, Any]], filename: str) -> str:
        _ensure_reports_dir()
        filepath = os.path.join(REPORTS_DIR, f"{filename}.txt")
        with open(filepath, mode='w', encoding='utf-8') as f:
            f.write("=== FINANCIAL REPORT ===\n\n")
            for item in data:
                f.write(f"[{item.get('date')}] {item.get('type')}: {item.get('amount')} {item.get('currency', 'KZT')} | Category: {item.get('category')} | {item.get('description')}\n")
        return filepath

class ReportExporterContext:
    def __init__(self, strategy: ReportExportStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ReportExportStrategy):
        self._strategy = strategy

    def generate_report(self, data: List[Dict[str, Any]], filename: str) -> str:
        return self._strategy.export(data, filename)
