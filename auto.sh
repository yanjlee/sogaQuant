#!/bin/bash
TODAY=`date +%Y%m%d`
echo $TODAY

python daily.py get_index_data $TODAY
echo "Stock Index done.\n"

#php /htdocs/quant/soga/mv/index.php Base get_fq_factor
#echo "FuQuan Done\n"

#php /htdocs/quant/soga/mv/index.php Base daily_stock_list
#echo "Stock daily done.\n"

python daily.py get_lhb_data $TODAY
echo "LHB stock list done.\n"

python daily.py summary_report $TODAY
echo "Stock Day_Report done.\n"

#python daily.py count_lhb_data $TODAY

#python multi.py get_multi_close_data $TODAY
#echo "Stock daily closing Bid.\n"

python daily.py summary_average $TODAY
echo "Average & MA_count Done."

#python daily.py get_macount $TODAY
#echo "MA_count Done."



#python main.py daily 20160620

#qiniu =======57781======
#runtime
#python realtime.py while_change
#python realtime.py get_min_data


#python realtime.py get_five_sb 1
#python realtime.py get_five_sb 2
#python realtime.py get_five_sb 3
#python realtime.py get_five_sb 4


#python realtime.py pankou 20160629
#python realtime.py realtime_pankou 2

#python wx.py get_baidu_words 3
#python wx.py get_baidu_words 1
#python wx.py get_baidu_words 2 46195

