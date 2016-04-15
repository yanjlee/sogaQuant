#!/bin/bash
TODAY=`date +%Y%m%d`
echo $TODAY

python daily.py get_index_data $TODAY
echo "Stock Index done.\n"

#php /htdocs/soga/trader/index.php Base get_fq_factor
#echo "FuQuan Done\n"

#php /htdocs/soga/trader/index.php Base daily_stock_list
#echo "Stock daily done.\n"


#php /htdocs/soga/trader/index.php Lhb code_list $TODAY
python daily.py get_lhb_data $TODAY
echo "LHB stock list done.\n"

#python multi.py get_day_lhb $TODAY
#echo "LHB stock detail done.\n"

python daily.py get_limit $TODAY
echo "Stock Day_Report done.\n"

#php /htdocs/soga/trader/index.php Lhb get_daily_lyb $TODAY
python daily.py count_lhb_data $TODAY

python multi.py get_multi_close_data $TODAY
echo "Stock daily closing Bid.\n"

python daily.py get_average $TODAY

python daily.py get_macount $TODAY
echo "MA_count Done."


#runtime
#python daily.py get_change 20160320
#python daily.py get_min_data

