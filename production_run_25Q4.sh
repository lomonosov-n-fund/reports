#!/bin/bash
year=2025
quarter=4
output_dir=./report 
report_date=2026-01-16
index_date=2026-01-15

python query-vault-activity.py --output-dir . --filename vault-activity.json    
python depositors.py --latex --quarter $quarter --year $year --output-dir $output_dir
python performance.py --latex --quarter $quarter --year $year --output-dir $output_dir
echo "Update ./historical-data and ./index"
python asset-allocation.py --latex --quarter $quarter --year $year --output-dir $output_dir --report-date $report_date --index-date $index_date
python expenses.py --latex --quarter $quarter --year $year --output-dir $output_dir

