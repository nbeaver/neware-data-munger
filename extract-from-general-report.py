#!/usr/bin/env python2.7
import sys
import os
import string

# TODO: dictionaries for associating values as strings to spreadsheet column letters.
#cycle_summary_dict = {'Cycle ID': 'A', 'Charge capacity [mAh]': 'B', 'Discharge capacity [mAh]': 'C'}

def colnum(column_name):
    if len(column_name) > 2:
        raise NotImplementedError
    for letter in column_name:
        if letter not in string.uppercase:
            raise ValueError
    
    column_letter_to_number_dict = {}
    for i, capital_letter in enumerate(string.uppercase):
        column_letter_to_number_dict[capital_letter] = i
    if len(column_name) == 1:
        return column_letter_to_number_dict[letter]
    elif len(column_name) == 2:
        first_letter = column_name[0]
        second_letter = column_name[1]
        return len(string.uppercase)*(1 + column_letter_to_number_dict[first_letter]) + column_letter_to_number_dict[second_letter]

# Since we start at zero, it should get to AA at column 26.
assert colnum('AA') == len(string.uppercase)

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

if len(sys.argv) > 1:
    input_file_path = sys.argv[1]
else:
    input_file_path = raw_input("Enter filename:")
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
    cycle_summary_file.write(header_comment_character + "CycleID charge capacity [mAh]"+output_delimiter+ "discharge capacity [mAh]\n")
    for i, line in enumerate(general_report):
        if i < header_lines_to_skip:
            continue # don't process header lines
        cols = line.split("\t")
        row_type = determine_row_type(cols)

        if row_type == "cycle_summary":
            cycle_id = cols[colnum('A')]
            print "Extracting cycle #",cycle_id
            capacity_charge = cols[colnum('C')]
            capacity_discharge = cols[colnum('D')]
            cycle_summary_file.write(output_delimiter.join([cycle_id, capacity_charge, capacity_charge]) + "\n")
        elif row_type == "step_settings":
            step_type = cols[colnum('E')].strip()
            #print step_type
            if step_type == "CC_Chg":
                filename = full_basename + "_charge_" + cycle_id + output_file_extension
                f = open(filename, 'w')
                f.write(header_comment_character+"mAh"+output_delimiter+"V\n")
            elif step_type == "CC_DChg":
                filename = full_basename + "_discharge_" + cycle_id + output_file_extension
                f = open(filename, 'w')
                f.write(header_comment_character+"mAh"+output_delimiter+"V\n")
        elif row_type == "cell_data":
            if step_type == "CC_Chg" or step_type == "CC_DChg":
                V = cols[colnum('I')]
                mAh = cols[colnum('O')]
                #print "line "+str(i)+" mAh: "+mAh
                f.write(mAh + output_delimiter + V + "\n")
                #print V, mAh

cycle_summary_file.close()
