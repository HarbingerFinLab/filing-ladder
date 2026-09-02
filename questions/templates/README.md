Template instantiations go here as `*.jsonl`, one `Question` per line. Example line:

{"id": "tpl-mmm-fy2024-001", "set": "templates", "question": "What was 3M's total capital expenditure in FY2024, per the consolidated statement of cash flows?", "gold_type": "numeric", "gold": "1,398", "gold_unit": "USD", "gold_scale": "millions", "tier": "T1", "stratum": "lookup", "category": "capex", "rubric": [], "gold_source": "document-read", "filing": {"cik": "0000066740", "accession": "0000066740-25-000006", "ticker": "MMM", "fiscal_year": 2024, "form": "10-K"}, "notes": "cash flow statement, 'Purchases of property, plant and equipment (PP&E)'"}

The example value above is illustrative; every committed gold is read from the document by a person.
