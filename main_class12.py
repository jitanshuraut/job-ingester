#!/usr/bin/env python3
"""
JEE Class 12 Physics Trend Analysis & 2027 Prediction Report
Main Orchestrator — builds all 15 sections into a single .docx
"""

import sys
import os

# Suppress intermediate save messages
sys.stdout = open(os.devnull, 'w')

# Import all part modules — each adds its sections to the shared `doc` from core
import build_report_class12_p1   # Sections 1-5 (also adds cover, exec summary, TOC)
import build_report_class12_p2   # Sections 6-10
import build_report_class12_p3   # Sections 11-15

sys.stdout = sys.__stdout__

# Import the shared doc object
from build_report_class12_core import doc

output_path = os.path.join(os.path.dirname(__file__), 'JEE_Class12_Physics_Trend_Analysis_2027_Prediction.docx')
doc.save(output_path)

para_count = len(doc.paragraphs)
table_count = len(doc.tables)
heading_count = sum(1 for p in doc.paragraphs if p.style.name.startswith('Heading'))

print(f'Document saved: {output_path}')
print(f'Paragraphs: {para_count}')
print(f'Tables: {table_count}')
print(f'Headings: {heading_count}')

import math
est_pages = math.ceil(para_count / 35) + table_count * 2
print(f'Estimated pages: ~{est_pages}')
