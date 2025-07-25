#!/bin/bash
year=2025
quarter=2
output_dir=./report 
report_date=2025-07-08
index_date=2025-07-07

python query-vault-activity.py --output-dir . --filename vault-activity.json    
python depositors.py --latex --quarter $quarter --year $year --output-dir $output_dir
python performance.py --latex --quarter $quarter --year $year --output-dir $output_dir
python asset-allocation.py --latex --quarter $quarter --year $year --output-dir $output_dir --report-date $report_date --index-date $index_date
python expenses.py --latex --quarter $quarter --year $year --output-dir $output_dir

