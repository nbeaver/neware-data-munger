all: scripted interactive readme.html
.PHONY : all scripted interactive

scripted:
	./extract_general_report.py --input example-data/extracted-from-BTSDA-2013-04-22/5days_cell2_BTSDA_export.csv
	./extract_general_report.py --input example-data/extracted-from-BTSDA-2013-04-22/MoO2_coin_cell_N1.csv --mass 6.56
	./extract_general_report.py --input example-data/extracted-from-BTSDA-2013-04-22/MoO2_coin_cell_N2.csv --mass 8.96
	./extract_general_report.py --input example-data/extracted-from-BTSDA-2013-04-22/MoO2_coin_cell_N3.csv --mass 0.96
	./extract_general_report.py --input example-data/extracted-from-BTSDA-2013-04-22/cell3_NMC_09_09.txt --mass 4.3
	./extract_general_report.py --input example-data/extracted-from-BtsControl/5days_cell2/5days_cell2_general_report_txt_export.csv
	./extract_general_report.py --input example-data/extracted-from-BtsControl/5days_cell2/5days_cell2_general_report_excel_export.csv
	./extract_general_report.py --input example-data/extracted-from-BtsControl/MoO2_coin_cell_N1/MoO2_coin_cell_N1_general_report.csv --mass 6.56
	./extract_general_report.py --input example-data/extracted-from-BtsControl/MoO2_coin_cell_N2/MoO2_coin_cell_N2_general_report.csv --mass 8.96

interactive:
	# Use `expect` to test interactive version.
	./interactive.exp

readme.html : readme.rst
	rst2html readme.rst > readme.html

clean:
	rm -rf example-data/extracted-from-BTSDA-2013-04-22/5days_cell2_BTSDA_export_data_extracted/
	rm -rf example-data/extracted-from-BTSDA-2013-04-22/MoO2_coin_cell_N1_data_extracted/
	rm -rf example-data/extracted-from-BTSDA-2013-04-22/MoO2_coin_cell_N2_data_extracted/
	rm -rf example-data/extracted-from-BTSDA-2013-04-22/MoO2_coin_cell_N3_data_extracted/
	rm -rf example-data/extracted-from-BTSDA-2013-04-22/MoO2_coin_cell_N3_data_extracted/
	rm -rf example-data/extracted-from-BTSDA-2013-04-22/cell3_NMC_09_09_data_extracted/
	rm -rf example-data/extracted-from-BtsControl/5days_cell2/5days_cell2_general_report_excel_export_data_extracted/
	rm -rf example-data/extracted-from-BtsControl/5days_cell2/5days_cell2_general_report_txt_export_data_extracted/
	rm -rf example-data/extracted-from-BtsControl/MoO2_coin_cell_N1/MoO2_coin_cell_N1_general_report_data_extracted/
	rm -rf example-data/extracted-from-BtsControl/MoO2_coin_cell_N2/MoO2_coin_cell_N2_general_report_data_extracted/
