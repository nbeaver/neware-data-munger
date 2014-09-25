#!/usr/bin/env python2.7
import sys
import os
import string
import argparse

# TODO: dictionaries for associating values as strings to spreadsheet column letters.
#cycle_summary_dict = {'Cycle ID': 'A', 'Charge capacity [mAh]': 'B', 'Discharge capacity [mAh]': 'C'}

# mapping for BTSDA 7.4.1.824 general report (.txt)
columns_BTSDA = {
    'cycle' : {
        'Cycle ID' : 'A',
        'Cycle charge capacity' : 'C',
        'Cycle discharge capacity' : 'E',
    },
    'step' : {
        'Step Index' : 'C',
        'Step type' : 'E',
        'Duration [H:MM:SS.000]' : 'F',
    },
    'record' : {
        'Record Index' : 'E',
        'Step time elapsed' : 'G',
        'V' : 'I',
        'mAh' : 'Q',
        'mA' : 'K',
        'Timestamp' : 'AA',
    },
}

# mapping for BtsControl general report (.txt)
columns_BtsControl = {
    'cycle' : {
        'Cycle ID' : 'A',
        'Cycle charge capacity [mAh]' : 'C',
        'Cycle discharge capacity [mAh]' : 'E',
    },
    'step' : {
        'Step Index' : 'C',
        'Step type' : 'E',
        'Duration [H:MM:SS.000]' : 'F',
        'Capacity [mAh]' : 'H',
    },
    'record' : {
        'Record Index' : 'E',
        'Step time elapsed' : 'G',
        'V' : 'I',
        'mA' : 'K',
        'mAh' : 'O',
        'mAh/g' : 'Q',
        'Timestamp' : 'W',
    },
}

# mapping for BtsControl general report (.xlsx exported to .tsv)
columns_BtsControl_xlsx = {
    'cycle' : {
        'Cycle ID' : 'A',
        'Cycle charge capacity [mAh]' : 'B',
        'Cycle discharge capacity [mAh]' : 'C',
    },
    'step' : {
        'Step Index' : 'B',
        'Step type' : 'C',
        'Duration [H:MM:SS.000]' : 'D',
        'Capacity [mAh]' : 'E',
    },
    'record' : {
        'Record Index' : 'C',
        'Step time elapsed' : 'D',
        'V' : 'E',
        'mA' : 'F',
        'mAh' : 'H',
        'mAh/g' : 'I',
        'Energy [mWh]' : 'J',
        'mWh/g' : 'K',
        'Timestamp' : 'L',
        'Power [W]' : 'P',

    },
}

def colnum(column_letter):
    """Given a column letter from A to ZZ, return a column number starting from 0."""
    assert type(column_letter) is str, "Column letter not a string:"+str(column_letter)+" is type "+str(type(column_letter))
    if len(column_letter) > 2:
        # We don't go past ZZ.
        raise NotImplementedError
    for letter in column_letter:
        if letter not in string.uppercase:
            raise ValueError
    
    column_letter_to_number_dict = {}
    for i, capital_letter in enumerate(string.uppercase):
        column_letter_to_number_dict[capital_letter] = i
    if len(column_letter) == 1:
        return column_letter_to_number_dict[letter]
    elif len(column_letter) == 2:
        first_letter = column_letter[0]
        second_letter = column_letter[1]
        return len(string.uppercase)*(1 + column_letter_to_number_dict[first_letter]) + column_letter_to_number_dict[second_letter]

# Since we start at zero, it should get to AA at column 26.
assert colnum('AA') == len(string.uppercase)

def colletter(column_number):
    """Given a column number starting from 0, return a column letter from A to ZZ."""
    assert type(column_number) is int, "Column number not an integer:"+str(column_number)+" is type "+str(type(column_number))
    if column_number > colnum('ZZ'): # 701, in case you're wondering.
        # We don't go past ZZ.
        raise NotImplementedError
    #TODO: deal with the fact that we may not just get capital letters.
    if column_number < len(string.uppercase):
        # Just one letter.
        return string.uppercase[column_number]
    else:
        # We have to subtract one since we want to go from Z to AA, not BA.
        first_letter = string.uppercase[(column_number / len(string.uppercase)) - 1]
        # We don't have to subtract one since modulo starts from 0.
        second_letter = string.uppercase[column_number % len(string.uppercase)]
        return first_letter + second_letter

assert colletter(len(string.uppercase)) == 'AA'

def infer_input_file_format(header_line):
    header_1_BtsControl_xlsx = "Cycle ID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	Specific Capacity-Chg(mAh/g)  	Specific Capacity-Dchg(mAh/g)  	Chg/DChg Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Plat_Cap(mAh)  	Plat_Capacity Density(mAh)  	Plat_Efficiency(%)  	Plat_Time(h:min:s.ms)  	Capacitance_Chg(mF)  	Capacitance_DChg(mF)  	IR(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(oC)  	"
    header_1_BtsControl = "Cycle ID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	Specific Capacity-Chg(mAh/g)  	Specific Capacity-Dchg(mAh/g)  	Chg/DChg Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Plat_Cap(mAh)  	Plat_Capacity Density(mAh)  	Plat_Efficiency(%)  	Plat_Time(h:min:s.ms)  	Capacitance_Chg(mF)  	Capacitance_DChg(mF)  	IR(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(oC)  	"
    header_1_BTSDA = "CycleID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	RCap_Chg(mAh/g)  	RCap_DChg(mAh/g)  	Charge/Discharge Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Platform_Cap(mAh)  	Platform_RCap(mAh)  	Platfrom_Efficiency(%)  	Platform_Time(h:min:s.ms)  	Capacitance_Chg(F)  	Capacitance_DChg(F)  	rd(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(?)  	"
    if header_line == header_1_BtsControl:
        return columns_BtsControl
    elif header_line == header_1_BtsControl_xlsx:
        return columns_BtsControl_xlsx
    elif header_line == header_1_BTSDA:
        return columns_BTSDA
def determine_row_type(row):
    is_cycle_summary_row = None
    is_step_settings_row = None
    is_data_row = None
    if row[colnum('A')] != "":
        is_cycle_summary_row = True
        is_step_settings_row = False
        is_data_row = False
    else:
        is_cycle_summary_row = False
        if row[colnum('C')] != "":
            is_step_settings_row = True
            is_data_row = False
        else:
            is_step_settings_row = False
            is_data_row = True
    row_types = [is_cycle_summary_row, is_step_settings_row, is_data_row]
    # Check that we didn't miss a type of row.
    assert all(row_type is not None for row_type in row_types)
    # Check that the row is one type and one type only.
    assert len([row_type for row_type in row_types if row_type]) == 1

    if is_cycle_summary_row:
        return "cycle_summary"
    elif is_step_settings_row:
        return "step_settings"
    elif is_data_row:
        return "cell_data"

def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='This is a script for processing data from a NEWARE battery cycler.')
        parser.add_argument('-m', '--mass', help='Plot title',required=False)
        parser.add_argument('-i', '--input', help='Input file',required=True)
        args = parser.parse_args()
        input_file_path = args.input
        if args.mass:
            mass_g = float(args.mass)/1000.0
        else:
            mass_g = None
    else:
        input_file_path = raw_input("Enter filename:")
        mass_input = raw_input("Enter mass of active material in mg, or just press enter to calculate mAh:")
        if mass_input != "":
            mass_g = float(mass_input)/1000.0
        else:
            mass_g = None

    input_file_path_no_extension = os.path.splitext(input_file_path)[0]
    basename_no_extension = os.path.splitext(os.path.basename(input_file_path))[0]
    folder_name = input_file_path_no_extension + "_data_extracted"
    print "Saving to folder",folder_name
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    full_basename = os.path.join(folder_name, basename_no_extension)

    with open(input_file_path) as general_report:
        header_lines_to_skip = 3
        step_type = None
        output_delimiter = '\t'
        header_comment_character = '#'
        output_file_extension = '.dat'
        cycle_summary_file = open(full_basename + "_all_cycle_summary" + output_file_extension, 'w')
        if mass_g:
            cycle_summary_file.write(header_comment_character + "CycleID charge capacity [mAh/g]"+output_delimiter+ "discharge capacity [mAh/g]\n")
        else:
            cycle_summary_file.write(header_comment_character + "CycleID charge capacity [mAh]"+output_delimiter+ "discharge capacity [mAh]\n")
        all_cycles = []
        for i, line in enumerate(general_report):
            if i < header_lines_to_skip:
                continue # don't process header lines
            cols = line.split("\t")
            row_type = determine_row_type(cols)

            if row_type == "cycle_summary":
                cycle_id = int(cols[colnum('A')])
                print "Extracting cycle #",str(cycle_id)
                capacity_charge = cols[colnum('C')]
                capacity_discharge = cols[colnum('E')]
                if mass_g:
                    specific_capacity_charge = float(capacity_charge)/(mass_g)
                    specific_capacity_discharge = float(capacity_discharge)/(mass_g)
                    cycle_summary_file.write(output_delimiter.join([str(cycle_id), str(specific_capacity_charge), str(specific_capacity_discharge)]) + "\n")
                else:
                    cycle_summary_file.write(output_delimiter.join([str(cycle_id), capacity_charge, capacity_charge]) + "\n")
            elif row_type == "step_settings":
                step_type = cols[colnum('E')].strip()
                #print step_type
                if step_type == "CC_Chg":
                    filename = full_basename + "_charge" + str(cycle_id) + output_file_extension
                    f = open(filename, 'w')
                    f.write(header_comment_character + "mAh/g" + output_delimiter + "V\n")
                elif step_type == "CC_DChg":
                    filename = full_basename + "_discharge" + str(cycle_id) + output_file_extension
                    f = open(filename, 'w')
                    f.write(header_comment_character + "mAh/g" + output_delimiter + "V\n")
            elif row_type == "cell_data":
                if step_type == "CC_Chg" or step_type == "CC_DChg":
                    V = cols[colnum('I')]
                    if mass_g:
                        mAh_per_g = str(float(cols[colnum('Q')])/(mass_g))
                    else:
                        mAh = cols[colnum('Q')]
                    assert V != ""
                    if mass_g:
                        assert mAh_per_g != ""
                    else:
                        assert mAh != ""
                    #print "line "+str(i)+" mAh: "+mAh
                    if mass_g:
                        f.write(mAh_per_g + output_delimiter + V + "\n")
                    else:
                        f.write(mAh + output_delimiter + V + "\n")
                    #print V, mAh

    cycle_summary_file.close()

if __name__ == "__main__":
    main()
