#!/bin/bash
TODAY=`date +%Y%m%d`
echo $TODAY

php /htdocs/soga/trader/index.php Base get_index_data
echo "Stock Index done.\n"

#php /htdocs/soga/trader/index.php Base get_fq_factor
#echo "FuQuan Done\n"

#php /htdocs/soga/trader/index.php Base daily_stock_list
#echo "Stock daily done.\n"


php /htdocs/soga/trader/index.php Lhb code_list $TODAY
echo "LHB stock list done.\n"

python multi.py get_day_lhb $TODAY
echo "LHB stock detail done.\n"

python daily.py k_day_report $TODAY
echo "Stock Day_Report done.\n"

php /htdocs/soga/trader/index.php Lhb get_daily_lyb $TODAY

python multi.py get_multi_close_data $TODAY
echo "Stock daily closing Bid.\n"

python daily.py k_average $TODAY

python daily.py k_ma_count $TODAY
echo "MA_count Done."

