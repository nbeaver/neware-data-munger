#!/usr/bin/env python2.7
# -*- encoding:utf-8 -*-
import sys
import os
import string
import argparse
import collections # for ordered dictionaries

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

def infer_input_file_format(input_file):
    header_line = input_file.readline()
    # Go back to the beginning of the file so we don't mess up code outside this function.
    input_file.seek(0)
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
        raise NotImplementedError, "Cannot recognize datafile type."

def determine_row_type(row, column_dict):
    is_cycle_row = None
    is_step_row = None
    is_record_row = None
    DEBUG = False
    if DEBUG:
        print row
        print "Looking at column ",column_dict['cycle']['Cycle ID']," which is '",row[colnum(column_dict['cycle']['Cycle ID'])],"'"
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

def parse_general_report(input_file_path):
    cycle_dict = collections.OrderedDict()
    # example structure:
    # cycle_dict[cycle_id]['charge']['V'] = ['1.22', '1.23', ...]

    DEBUG = False
    with open(input_file_path) as general_report:
        column_dict = infer_input_file_format(general_report)
        assert 'Cycle discharge capacity [mAh]' in column_dict['cycle'].keys()
        assert 'Voltage [V]' in column_dict['record'].keys()
        if 'Specific capacity [mAh/g]' in column_dict['record'].keys():
            vars_to_get = ['V', 'mAh', 'mAh/g']
        else:
            vars_to_get = ['V', 'mAh']
        header_lines_to_skip = 3
        step_type = None
        delimiter = '\t'
        for i, line in enumerate(general_report):
            if i < header_lines_to_skip:
                continue # don't process header lines
            cols = line.split(delimiter)
            row_type = determine_row_type(cols, column_dict)
            if row_type == "cycle":
                cycle_id = int(cols[colnum(column_dict[row_type]['Cycle ID'])])
                assert cycle_id not in cycle_dict.keys()
                if DEBUG:
                    print "Parsing cycle #",cycle_id
                cycle_dict[cycle_id] = {}
                capacity_charge = cols[colnum(column_dict[row_type]['Cycle charge capacity [mAh]'])]
                cycle_dict[cycle_id]['Cycle charge capacity [mAh]'] = capacity_charge
                capacity_discharge = cols[colnum(column_dict[row_type]['Cycle discharge capacity [mAh]'])]
                cycle_dict[cycle_id]['Cycle discharge capacity [mAh]'] = capacity_discharge
            elif row_type == "step":
                step_type = cols[colnum(column_dict[row_type]['Step type'])].strip()
                if step_type == "CC_Chg":
                    cycle_dict[cycle_id]['charge'] = {}
                    for var in vars_to_get:
                        cycle_dict[cycle_id]['charge'][var] = []
                elif step_type == "CC_DChg":
                    cycle_dict[cycle_id]['discharge'] = {}
                    for var in vars_to_get:
                        cycle_dict[cycle_id]['discharge'][var] = []
                elif step_type == "Rest":
                    pass
                else:
                    raise ValueError, "Unrecognized step type:" + step_type
            elif row_type == "record":
                V = cols[colnum(column_dict[row_type]['Voltage [V]'])]
                assert V != ""
                mAh = cols[colnum(column_dict[row_type]['Capacity [mAh]'])]
                assert mAh != ""
                if 'mAh/g' in vars_to_get:
                    mAh_per_g = cols[colnum(column_dict['record']['Specific capacity [mAh/g]'])]
                    assert mAh_per_g != ""
                if step_type == "CC_Chg" :
                    cycle_dict[cycle_id]['charge']['V'].append(V)
                    cycle_dict[cycle_id]['charge']['mAh'].append(mAh)
                    if 'mAh/g' in vars_to_get:
                        cycle_dict[cycle_id]['charge']['mAh/g'].append(mAh_per_g)
                elif step_type == "CC_DChg":
                    cycle_dict[cycle_id]['discharge']['V'].append(V)
                    cycle_dict[cycle_id]['discharge']['mAh'].append(mAh)
                    if 'mAh/g' in vars_to_get:
                        cycle_dict[cycle_id]['discharge']['mAh/g'].append(mAh_per_g)
                elif step_type == "Rest":
                    pass
                else:
                    raise ValueError, "Unrecognized step type:" + step_type
    return cycle_dict

def infer_mass(cycle_dict):
    # Look at the first charge cycle.
    #TODO: is there a way to make this less arbitrary?
    if 'mAh/g' in cycle_dict[1]['charge'].keys():
        # We can't take the first value, because it starts at 0.
        # The last value gets the best precision.
        length = len(cycle_dict[1]['charge']['mAh/g'])
        mAh_per_g = float(cycle_dict[1]['charge']['mAh/g'][length - 1])
        mAh = float(cycle_dict[1]['charge']['mAh'][length - 1])
        if mAh_per_g == 0.0:
            return None
        candidate_mass_g = mAh / mAh_per_g
        assert candidate_mass_g > 0
        return candidate_mass_g
    else:
        return None

def calculate_specific_capacities(cycle_dict, mass_g):
    """ This takes the mass as a float and puts the specific capacities in as strings."""
    assert mass_g > 0
    if 'mAh/g' in cycle_dict[1]['charge'].keys():
        print "Warning: overwriting exisitng specific capacities."
    #TODO: may need to split this into cycle summary calculations and record calculations.
    for cycle_id in cycle_dict.keys():

        capacity_charge = float(cycle_dict[cycle_id]['Cycle charge capacity [mAh]'])
        cycle_dict[cycle_id]['Cycle charge capacity [mAh/g]'] = str(capacity_charge / mass_g)

        capacity_discharge = float(cycle_dict[cycle_id]['Cycle discharge capacity [mAh]'])
        cycle_dict[cycle_id]['Cycle discharge capacity [mAh/g]'] = str(capacity_discharge / mass_g)

        cycle_dict[cycle_id]['charge']['mAh/g'] = []
        for mAh in cycle_dict[cycle_id]['charge']['mAh']:
            cycle_dict[cycle_id]['charge']['mAh/g'].append(str(float(mAh)/mass_g))

        try:
            cycle_dict[cycle_id]['discharge']['mAh/g'] = []
            for mAh in cycle_dict[cycle_id]['discharge']['mAh']:
                cycle_dict[cycle_id]['discharge']['mAh/g'].append(str(float(mAh)/mass_g))
        except KeyError:
            print "Warning: no discharge for cycle #"+str(cycle_id)+"."

def write_cycle_summary_file(cycle_dict, mass_g, filename):
    cycle_summary_file = open(filename, 'w')
    header_comment_character = '#'
    delimiter = '\t'
    if mass_g:
        capacity_type = "[mAh/g]"
    else:
        capacity_type = "[mAh]"

    cycle_summary_file.write(header_comment_character + "CycleID"  + delimiter)
    cycle_summary_file.write("charge capacity "    + capacity_type + delimiter)
    cycle_summary_file.write("discharge capacity " + capacity_type + "\n")

    for cycle_id in cycle_dict.keys():
        if mass_g == None:
            capacity_charge = cycle_dict[cycle_id]['Cycle charge capacity [mAh]']
            capacity_discharge = cycle_dict[cycle_id]['Cycle discharge capacity [mAh]']
        else:
            capacity_charge = float(cycle_dict[cycle_id]['Cycle charge capacity [mAh]']) / mass_g
            capacity_discharge = float(cycle_dict[cycle_id]['Cycle discharge capacity [mAh]']) / mass_g

        cycle_summary_file.write(delimiter.join([str(cycle_id), str(capacity_charge), str(capacity_discharge)]) + "\n")

    cycle_summary_file.close()

def write_individual_cycle_file(x_list, x_name, y_list, y_name, filename):
    header_comment_character = '#'
    delimiter = '\t'
    outfile = open(filename, 'w')
    outfile.write(header_comment_character + x_name + delimiter + y_name + "\n")
    for x, y in zip(x_list, y_list):
        assert x != ""
        assert y != ""
        outfile.write(x + delimiter + y + "\n")
    outfile.close()

def write_grace_input_file(cycle_dict, filename):
    grace_input_file = open(filename, 'w')
    delimiter = ' '
    record_separator = '\n'
    for cycle_id in cycle_dict.keys():
        def write_step(x_list, y_list, step_type):
            for x, y in zip(x_list, y_list):
                grace_input_file.write(x + delimiter + y + "\n")
            grace_input_file.write(record_separator)

        step_type = 'charge'
        write_step(cycle_dict[cycle_id][step_type]['mAh'], cycle_dict[cycle_id][step_type]['V'], step_type)
        step_type = 'discharge'
        try:
            write_step(cycle_dict[cycle_id][step_type]['mAh'], cycle_dict[cycle_id][step_type]['V'], step_type)
        except KeyError:
            print "Warning: no discharge for cycle #",cycle_id

    grace_input_file.close()

def write_origin_input_file(cycle_dict, filename):
    origin_input_file = open(filename, 'w')
    origin_input_file.close()

#TODO: split this gigantic function into smaller pieces
def main():
    require_mass_calculations = None
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='This is a script for processing data from a NEWARE battery cycler.')
        parser.add_argument('-m', '--mass', help='Plot title',required=False)
        parser.add_argument('-i', '--input', help='Input file',required=True)
        args = parser.parse_args()
        input_file_path = args.input
        cycle_dict = parse_general_report(input_file_path)
        if args.mass:
            # TODO: warn if this mass conflicts with inferred mass.
            require_mass_calculations = True
            mass_g = float(args.mass)/1000.0
        else:
            mass_g = infer_mass(cycle_dict)
            require_mass_calculations = False
    else:
        # DONE: see if we can infer the mass from the data.
        input_file_path = raw_input("Enter filename:")
        cycle_dict = parse_general_report(input_file_path)
        mass_g = infer_mass(cycle_dict)
        if mass_g == None:
            mass_input = raw_input("Enter mass of active material in mg, or just press enter to calculate mAh:")
            if mass_input != "":
                #TODO: test for 0 mass and ask for new input.
                mass_g = float(mass_input)/1000.0
                require_mass_calculations = True
            else:
                mass_g = None
                require_mass_calculations = False
        else:
            print "Mass is inferred to be ",mass_g*1000,' mg.'
            #TODO: prompt to ask the user if this is ok.

    #TODO: calculate mAh/g from mass_g and add it to the cycle_dict.
    if require_mass_calculations:
        calculate_specific_capacities(cycle_dict, mass_g)

    input_file_path_no_extension = os.path.splitext(input_file_path)[0]
    basename_no_extension = os.path.splitext(os.path.basename(input_file_path))[0]
    folder_name = input_file_path_no_extension + "_data_extracted"
    print "Saving to folder",folder_name
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    full_basename = os.path.join(folder_name, basename_no_extension)

    write_cycle_summary_file(cycle_dict, mass_g, full_basename+"_all_cycle_summary.dat")

    for cycle_id in cycle_dict.keys():
        if mass_g == None:
            capacity_type = 'mAh'
        else:
            capacity_type = 'mAh/g'

        def write_cycle(cycle, step_type):
            write_individual_cycle_file(cycle[capacity_type], capacity_type, \
                                        cycle['V'], 'V', \
                                        full_basename + "_" + step_type + str(cycle_id) + ".dat")

        this_cycle = cycle_dict[cycle_id]['charge']
        write_cycle(this_cycle, 'charge')

        try:
            this_cycle = cycle_dict[cycle_id]['discharge']
            write_cycle(this_cycle, 'discharge')
        except KeyError:
            print "Warning: no discharge for cycle #",str(cycle_id),"."

    write_grace_input_file(cycle_dict, full_basename + "_grace_ascii.dat")
    write_origin_input_file(cycle_dict, full_basename + "_origin_columnar.csv")

if __name__ == "__main__":
    main()
