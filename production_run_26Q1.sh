#!/bin/bash
year=2026
quarter=1
output_dir=./report 
report_date=2026-04-09
index_date=2026-04-09

python query-vault-activity.py --output-dir . --filename vault-activity.json    
python depositors.py --latex --quarter $quarter --year $year --output-dir $output_dir
python performance.py --latex --quarter $quarter --year $year --output-dir $output_dir
echo "Don't forget to update ./historical-data and ./index"
python asset-allocation.py --latex --quarter $quarter --year $year --output-dir $output_dir --report-date $report_date --index-date $index_date
python expenses.py --latex --quarter $quarter --year $year --output-dir $output_dir

