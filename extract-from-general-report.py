#!/usr/bin/env python2.7
# -*- encoding:utf-8 -*-
import sys
import os
import string
import argparse

# DONE: dictionaries for associating values as strings to spreadsheet column letters.

# mapping for BTSDA 7.4.1.824 general report (.txt)
columns_BTSDA = {
    'cycle' : {
        'Cycle ID' : 'A',
        'Cycle charge capacity [mAh]' : 'C',
        'Cycle discharge capacity [mAh]' : 'E',
    },
    'step' : {
        'Step ID' : 'C',
        'Step type' : 'E',
        'Duration [H:MM:SS.000]' : 'F',
    },
    'record' : {
        'Record ID' : 'E',
        'Step time elapsed' : 'G',
        'Voltage [V]' : 'I',
        'Capacity [mAh]' : 'Q',
        'Current [mA]' : 'K',
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
        'Step ID' : 'C',
        'Step type' : 'E',
        'Duration [H:MM:SS.000]' : 'F',
        'Capacity [mAh]' : 'H',
    },
    'record' : {
        'Record ID' : 'E',
        'Step time elapsed' : 'G',
        'Voltage [V]' : 'I',
        'Current [mA]' : 'K',
        'Capacity [mAh]' : 'O',
        'Specific capacity [mAh/g]' : 'Q',
        'Energy [mWh]' : 'S',
        'Energy density [mWh/g]' : 'U',
        'Timestamp' : 'W',
        'Power [W]' : 'AE',
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
        'Step ID' : 'B',
        'Step type' : 'C',
        'Duration [H:MM:SS.000]' : 'D',
        'Capacity [mAh]' : 'E',
    },
    'record' : {
        'Record ID' : 'C',
        'Step time elapsed' : 'D',
        'Voltage [V]' : 'E',
        'Current [mA]' : 'F',
        'Capacity [mAh]' : 'H',
        'Specific capacity [mAh/g]' : 'I',
        'Energy [mWh]' : 'J',
        'Energy density [mWh/g]' : 'K',
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
    header_line = header_line.strip()
    #header_1_BtsControl_xlsx = "Cycle ID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	Specific Capacity-Chg(mAh/g)  	Specific Capacity-Dchg(mAh/g)  	Chg/DChg Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Plat_Cap(mAh)  	Plat_Capacity Density(mAh)  	Plat_Efficiency(%)  	Plat_Time(h:min:s.ms)  	Capacitance_Chg(mF)  	Capacitance_DChg(mF)  	IR(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(oC)"
    header_1_BtsControl_xlsx = "Cycle ID	Cap_Chg(mAh)	Cap_DChg(mAh)	Specific Capacity-Chg(mAh/g)	Specific Capacity-Dchg(mAh/g)	Chg/DChg Efficiency(%)	Engy_Chg(mWh)	Engy_DChg(mWh)	REngy_Chg(mWh/g)	REngy_Dchg(mWh/g)	CC_Chg_Ratio(%)	CC_Chg_Cap(mAh)	Plat_Cap(mAh)	Plat_Capacity Density(mAh)	Plat_Efficiency(%)	Plat_Time(h:min:s.ms)	Capacitance_Chg(mF)	Capacitance_DChg(mF)	IR(mΩ)	Mid_value Voltage(V)	Discharge Fading Ratio(%)	Charge Time(h:min:s.ms)	Discharge Time(h:min:s.ms)	Charge IR(mΩ)	Discharge IR(mΩ)	End Temperature(oC)"
    header_1_BtsControl = "Cycle ID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	Specific Capacity-Chg(mAh/g)  	Specific Capacity-Dchg(mAh/g)  	Chg/DChg Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Plat_Cap(mAh)  	Plat_Capacity Density(mAh)  	Plat_Efficiency(%)  	Plat_Time(h:min:s.ms)  	Capacitance_Chg(mF)  	Capacitance_DChg(mF)  	IR(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(oC)"
    header_1_BTSDA = "CycleID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	RCap_Chg(mAh/g)  	RCap_DChg(mAh/g)  	Charge/Discharge Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Platform_Cap(mAh)  	Platform_RCap(mAh)  	Platfrom_Efficiency(%)  	Platform_Time(h:min:s.ms)  	Capacitance_Chg(F)  	Capacitance_DChg(F)  	rd(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(?)"
    if header_line == header_1_BtsControl:
        return columns_BtsControl
    elif header_line == header_1_BtsControl_xlsx:
        return columns_BtsControl_xlsx
    elif header_line == header_1_BTSDA:
        return columns_BTSDA
    else:
        print "Header line is:",header_line
        raise NotImplementedError, "Cannot recognize datafile type."

def determine_row_type(row, column_dict):
    is_cycle_row = None
    is_step_row = None
    is_record_row = None
    if row[colnum(column_dict['cycle']['Cycle ID'])] != "":
        is_cycle_row = True
        is_step_row = False
        is_record_row = False
    else:
        is_cycle_row = False
        if row[colnum(column_dict['step']['Step ID'])] != "":
            is_step_row = True
            is_record_row = False
        else:
            is_step_row = False
            if row[colnum(column_dict['record']['Record ID'])] != "":
                is_record_row = True
            else:
                raise ValueError, "Cannot determine row type for this row:"+row
    row_types = [is_cycle_row, is_step_row, is_record_row]
    # Check that we didn't miss a type of row.
    assert all(row_type is not None for row_type in row_types)
    # Check that the row is one type and one type only.
    assert len([row_type for row_type in row_types if row_type]) == 1

    if is_cycle_row:
        return "cycle"
    elif is_step_row:
        return "step"
    elif is_record_row:
        return "record"

#TODO: split this gigantic function into smaller pieces
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
        # TODO: see if we can infer the mass from the data.
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

    # TODO: split this off into a separate function.
    with open(input_file_path) as general_report:
        column_dict = infer_input_file_format(general_report.readline())
        # Try to infer the mass.
        # TODO: separate this out to make it less messy.
        # TODO: restructure this to avoid the duplication of later code.
        if mass_g == None:
            if 'Specific capacity [mAh/g]' in column_dict['record'].keys():
                for i, line in enumerate(general_report.readlines()):
                    if i < 2:
                        pass
                    else:
                        cols = line.split("\t")
                        if determine_row_type(cols, column_dict) == 'record':
                            mAh = float(cols[colnum(column_dict['record']['Capacity [mAh]'])])
                            mAh_per_g = float(cols[colnum(column_dict['record']['Specific capacity [mAh/g]'])])
                            if mAh_per_g == 0.0:
                                pass
                            else:
                                print "mAh =",str(mAh)
                                print "mAh/g =",str(mAh_per_g)
                                candidate_mass_g = mAh / mAh_per_g
                                break
                            # We've found a record, so let's break out of the for loop.
                assert candidate_mass_g > 0
                print "Data assumes mass of ",str(1000*candidate_mass_g),"mg."
                print "Using this mass for calculations."
        # Return to first byte of the file.
        general_report.seek(0)
        header_lines_to_skip = 3
        step_type = None
        output_delimiter = '\t'
        header_comment_character = '#'
        output_file_extension = '.dat'
        cycle_summary_file = open(full_basename + "_all_cycle_summary" + output_file_extension, 'w')
        grace_output_file = open(full_basename + "_grace_ascii.dat", 'w')
        if mass_g:
            cycle_summary_file.write(header_comment_character + "CycleID charge capacity [mAh/g]"+output_delimiter+ "discharge capacity [mAh/g]\n")
        else:
            cycle_summary_file.write(header_comment_character + "CycleID charge capacity [mAh]"+output_delimiter+ "discharge capacity [mAh]\n")
        all_cycles = []
        for i, line in enumerate(general_report):
            if i < header_lines_to_skip:
                continue # don't process header lines
            cols = line.split("\t")
            row_type = determine_row_type(cols, column_dict)
            if row_type == "cycle":
                cycle_id = int(cols[colnum(column_dict[row_type]['Cycle ID'])])
                print "Extracting cycle #",str(cycle_id)
                capacity_charge = cols[colnum(column_dict[row_type]['Cycle charge capacity [mAh]'])]
                capacity_discharge = cols[colnum(column_dict[row_type]['Cycle discharge capacity [mAh]'])]
                if mass_g:
                    specific_capacity_charge = float(capacity_charge)/(mass_g)
                    specific_capacity_discharge = float(capacity_discharge)/(mass_g)
                    cycle_summary_file.write(output_delimiter.join([str(cycle_id), str(specific_capacity_charge), str(specific_capacity_discharge)]) + "\n")
                else:
                    cycle_summary_file.write(output_delimiter.join([str(cycle_id), capacity_charge, capacity_charge]) + "\n")
                grace_output_file.write("\n")
            elif row_type == "step":
                step_type = cols[colnum(column_dict[row_type]['Step type'])].strip()
                #print step_type
                grace_output_file.write("\n")
                if step_type == "CC_Chg":
                    filename = full_basename + "_charge" + str(cycle_id) + output_file_extension
                    f = open(filename, 'w')
                    f.write(header_comment_character + "mAh/g" + output_delimiter + "V\n")
                elif step_type == "CC_DChg":
                    filename = full_basename + "_discharge" + str(cycle_id) + output_file_extension
                    f = open(filename, 'w')
                    f.write(header_comment_character + "mAh/g" + output_delimiter + "V\n")
                elif step_type == "Rest":
                    pass
                else:
                    raise ValueError, "Unrecognized step type:" + step_type
            elif row_type == "record":
                if step_type == "CC_Chg" or step_type == "CC_DChg":
                    V = cols[colnum(column_dict[row_type]['Voltage [V]'])]
                    assert V != ""
                    mAh = cols[colnum(column_dict[row_type]['Capacity [mAh]'])]
                    assert mAh != ""

                    if mass_g:
                        mAh_per_g = str(float(mAh)/(mass_g))
                        assert mAh_per_g != ""
                    #print "line "+str(i)+" mAh: "+mAh
                    if mass_g:
                        f.write(mAh_per_g + output_delimiter + V + "\n")
                        grace_output_file.write(mAh_per_g + " " + V + "\n")
                    else:
                        f.write(mAh + output_delimiter + V + "\n")
                        grace_output_file.write(mAh + " " + V + "\n")
                    #print V, mAh
                elif step_type == "Rest":
                    pass
                else:
                    raise ValueError, "Unrecognized step type:" + step_type

    cycle_summary_file.close()
    grace_output_file.close()

if __name__ == "__main__":
    main()
