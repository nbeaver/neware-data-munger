#!/usr/bin/env python2
# -*- encoding:utf-8 -*-
from __future__ import print_function
import sys
import os
import string
import argparse
import collections # for ordered dictionaries
import distutils.util # for strtobool
import ConfigParser
import logging

# DONE: dictionaries for associating values as strings to spreadsheet column letters.

columns_BTSDA = {
    'description' : 'BTSDA 7.4.1.824 general report (.txt)',
    'headers': [
        "CycleID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	RCap_Chg(mAh/g)  	RCap_DChg(mAh/g)  	Charge/Discharge Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Platform_Cap(mAh)  	Platform_RCap(mAh)  	Platfrom_Efficiency(%)  	Platform_Time(h:min:s.ms)  	Capacitance_Chg(F)  	Capacitance_DChg(F)  	rd(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(?)",
        "Cycle Index  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	Capacity Density_Chg(mAh/g)  	Capacity Density_DChg(mAh/g)  	Charge/Discharge Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Plat_Cap(mAh)  	Plat_Capacity Density(mAh)  	Plat_Efficiency(%)  	Plat_Time(h:min:s.ms)  	Capacitance_Chg(F)  	Capacitance_DChg(F)  	rd(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(°C)",
    "Cycle ID		Cap_Chg(mAh)		Cap_DChg(mAh)		Specific Capacity-Chg(mAh/g)	Specific Capacity-Dchg(mAh/g)	Chg/DChg Efficiency(%)	Engy_Chg(mWh)		Engy_DChg(mWh)		REngy_Chg(mWh/g)	REngy_Dchg(mWh/g)	CC_Chg_Ratio(%)		CC_Chg_Cap(mAh)		Plat_Cap(mAh)		Plat_Capacity Density(mAh/g)	Plat_Efficiency(%)	Plat_Time(h:min:s.ms)	Capacitance_Chg(F)	Capacitance_DChg(F)	IR(mO)			Mid_value Voltage(V)	Discharge Fading Ratio(%)	Charge Time(h:min:s.ms)	Discharge Time(h:min:s.ms)	Charge IR(mO)		Discharge IR(mO)	End Temperature(oC)	Net Cap_DChg(mAh)	Net Engy_DChg(mWh)	",
    ],
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
        'Capacity [uAh]' : 'S',
        'Current [mA]' : 'K',
        'Timestamp' : 'AA',
    },
}

columns_BtsControl = {
    'description' : 'BTS TestControl 5.3.0013(2010.6.2) general report (.txt)',
    'headers': [
        "Cycle ID  	Cap_Chg(mAh)  	Cap_DChg(mAh)  	Specific Capacity-Chg(mAh/g)  	Specific Capacity-Dchg(mAh/g)  	Chg/DChg Efficiency(%)  	Engy_Chg(mWh)  	Engy_DChg(mWh)  	REngy_Chg(mWh/g)  	REngy_Dchg(mWh/g)  	CC_Chg_Ratio(%)  	CC_Chg_Cap(mAh)  	Plat_Cap(mAh)  	Plat_Capacity Density(mAh)  	Plat_Efficiency(%)  	Plat_Time(h:min:s.ms)  	Capacitance_Chg(mF)  	Capacitance_DChg(mF)  	IR(mO)  	Mid_value Voltage(V)  	Discharge Fading Ratio(%)  	Charge Time(h:min:s.ms)  	Discharge Time(h:min:s.ms)  	Charge IR(mO)  	Discharge IR(mO)  	End Temperature(oC)",
    ],
    'cycle' : {
        'Cycle ID' : 'A',
        'Cycle charge capacity [mAh]' : 'C',
        'Cycle discharge capacity [mAh]' : 'E',
        'Charge energy [mWh]' : 'M',
        'Discharge energy [mWh]' : 'O',
    },
    'step' : {
        'Step ID' : 'C',
        'Step type' : 'E',
        'Duration [H:MM:SS.000]' : 'F',
        'Capacity [mAh]' : 'H',
        'Energy [mWh]' : 'L',
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

columns_BtsControl_xlsx = {
    'description' : 'BTS TestControl 5.3.0013(2010.6.2) general report (.xlsx exported to .tsv)',
    'headers': [
        "Cycle ID	Cap_Chg(mAh)	Cap_DChg(mAh)	Specific Capacity-Chg(mAh/g)	Specific Capacity-Dchg(mAh/g)	Chg/DChg Efficiency(%)	Engy_Chg(mWh)	Engy_DChg(mWh)	REngy_Chg(mWh/g)	REngy_Dchg(mWh/g)	CC_Chg_Ratio(%)	CC_Chg_Cap(mAh)	Plat_Cap(mAh)	Plat_Capacity Density(mAh)	Plat_Efficiency(%)	Plat_Time(h:min:s.ms)	Capacitance_Chg(mF)	Capacitance_DChg(mF)	IR(mΩ)	Mid_value Voltage(V)	Discharge Fading Ratio(%)	Charge Time(h:min:s.ms)	Discharge Time(h:min:s.ms)	Charge IR(mΩ)	Discharge IR(mΩ)	End Temperature(oC)",
    ],
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


unknown_format_1 = {
    'description' : 'Unknown format #1',
    'headers': [
        "Cycle ID		Cap_Chg(mAh)		Cap_DChg(mAh)		Specific Capacity-Chg(mAh/g)	Specific Capacity-Dchg(mAh/g)	Chg/DChg Efficiency(%)	Engy_Chg(mWh)		Engy_DChg(mWh)		REngy_Chg(mWh/g)	REngy_Dchg(mWh/g)	CC_Chg_Ratio(%)		CC_Chg_Cap(mAh)		Plat_Cap(mAh)		Plat_Capacity Density(mAh/g)	Plat_Efficiency(%)	Plat_Time(h:min:s.ms)	Capacitance_Chg(F)	Capacitance_DChg(F)	IR(mO)			Mid_value Voltage(V)	Discharge Fading Ratio(%)	Charge Time(h:min:s.ms)	Discharge Time(h:min:s.ms)	Charge IR(mO)		Discharge IR(mO)	End Temperature(oC)	Net Cap_DChg(mAh)	Net Engy_DChg(mWh)"
    ],
    'cycle' : {
        'Cycle ID' : 'A',
        'Cycle charge capacity [mAh]' : 'D',
        'Cycle discharge capacity [mAh]' : 'G',
        'Charge/Discharge Efficiency [%]' : 'P',
        'Charge energy [mWh]' : 'S',
        'Discharge energy [mWh]' : 'V',
    },
    'step' : {
        'Step ID' : 'D',
        'Step type' : 'G',
        'Capacity [mAh]' : 'K',
        'Energy [mWh]': 'Q',
        'Start Voltage [V]' : 'Y',
        'End Voltage [V]' : 'AB',
    },
    'record' : {
        'Record ID' : 'G',
        'Voltage [V]' : 'L',
        'Current [mA]' : 'O',
        'Capacity [mAh]' : 'U',
        'Energy [mWh]' : 'AA',
        'Timestamp' : 'AF',
    },
}
# TODO: check Step type makes sense, e.g. 'Rest', 'CC_Chg', 'CC_DChg'
# TODO: be better about sniffing headers.

data_formats = [columns_BTSDA, columns_BtsControl, columns_BtsControl_xlsx, unknown_format_1]

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
    for data_format in data_formats:
        for known_header in data_format['headers']:
            if header_line == known_header:
                return data_format
    else:
        raise NotImplementedError("Cannot recognize datafile type.")

def determine_row_type(row, column_dict):
    # TODO: use a better data structure, maybe an enum.
    is_cycle_row = None
    is_step_row = None
    is_record_row = None
    logging.debug("Inspecting column {} in row {} for Cycle ID".format(column_dict['cycle']['Cycle ID'], row[colnum(column_dict['cycle']['Cycle ID'])]))
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
                raise ValueError("Cannot determine row type for this row: {}".format(row))
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

    with open(input_file_path) as general_report:
        column_dict = infer_input_file_format(general_report)
        logging.info("Detected data format '{}'".format(column_dict['description']))
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
                logging.debug("Parsing cycle #".format(cycle_id))

                cycle_dict[cycle_id] = {}

                capacity_charge_string = cols[colnum(column_dict[row_type]['Cycle charge capacity [mAh]'])]
                try:
                    capacity_charge = float(capacity_charge_string)
                except ValueError:
                    logging.error("Improper value for cycle charge capacity on line {}: {}".format(i, capacity_charge_string))
                    raise

                cycle_dict[cycle_id]['Cycle charge capacity [mAh]'] = capacity_charge

                capacity_discharge_string = cols[colnum(column_dict[row_type]['Cycle discharge capacity [mAh]'])]
                try:
                    capacity_discharge = float(capacity_discharge_string)
                except ValueError:
                    logging.error("Improper value for cycle discharge capacity on line {}: {}".format(i, capacity_discharge_string))
                    raise

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
                elif step_type == "CV_Chg":
                    # TODO: handle this properly
                    pass
                else:
                    raise ValueError, "Unrecognized step type:" + step_type
            elif row_type == "record":
                V = cols[colnum(column_dict[row_type]['Voltage [V]'])]
                assert V != ""
                try:
                    uAh = cols[colnum(column_dict[row_type]['Capacity [uAh]'])]
                    assert uAh != ""
                    mAh = str(float(uAh)/1000.0)
                except KeyError:
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
                elif step_type == "CV_Chg":
                    # TODO: handle this properly
                    pass
                else:
                    raise ValueError, "Unrecognized step type:" + step_type
    return cycle_dict

def infer_mass(cycle_dict):
    # Look at the first charge cycle.
    #TODO: is there a way to make this less arbitrary?
    for i in range(0, len(cycle_dict)):
        try:
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
        except KeyError:
            continue

def calculate_specific_capacities(cycle_dict, mass_g):
    """ This takes the mass as a float and puts the specific capacities in as strings."""
    assert mass_g > 0
    try:
        if 'mAh/g' in cycle_dict[1]['charge'].keys():
            logging.warning("Overwriting existing specific capacities.")
    except KeyError:
        pass
    #TODO: may need to split this into cycle summary calculations and record calculations.
    for cycle_id in cycle_dict.keys():
        for step_type in ['charge', 'discharge']:
            capacity = cycle_dict[cycle_id]['Cycle '+step_type+' capacity [mAh]']
            cycle_dict[cycle_id]['Cycle '+step_type+' capacity [mAh/g]'] = str(capacity / mass_g)

            try:
                cycle_dict[cycle_id][step_type]['mAh/g'] = []
                for mAh in cycle_dict[cycle_id][step_type]['mAh']:
                    cycle_dict[cycle_id][step_type]['mAh/g'].append(str(float(mAh)/mass_g))
            except KeyError:
                logging.warning("No {} for cycle #{}".format(step_type, cycle_id))

def write_ini_file(data_path, cycle_dict, mass_g, path, filename_prefix):
    filename = filename_prefix + "_data.ini"
    filepath = os.path.join(path, filename)
    config = ConfigParser.RawConfigParser()
    config.add_section('DataInfo')
    config.set('DataInfo', 'data_file', data_path)
    config.set('DataInfo', 'mass_grams', str(mass_g))
    config.set('DataInfo', 'cycles', str(len(cycle_dict)))
    # TODO: add field for date and time.
    # TODO: add field for type of data file.
    with open(filepath, 'wb') as configfile:
        config.write(configfile)

def write_cycle_summary_file(cycle_dict, mass_g, path, filename_prefix):
    filename = filename_prefix + "_all_cycle_summary.dat"
    filepath = os.path.join(path, filename)
    cycle_summary_file = open(filepath, 'w')
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

def write_grace_cycle_summary(cycle_dict, capacity_type, path, filename_prefix):
    assert capacity_type == 'mAh' or capacity_type == 'mAh/g'
    filename = filename_prefix + "_grace_cycle_summary.dat"
    filepath = os.path.join(path, filename)
    fp = open(filepath, 'w')

    def write_cycles(cycle_key):
        for cycle_id in cycle_dict.keys():
            capacity = cycle_dict[cycle_id][cycle_key]
            fp.write('{} {}\n'.format(cycle_id, capacity))

    write_cycles('Cycle charge capacity ['+capacity_type+']')
    fp.write('\n')
    write_cycles('Cycle discharge capacity ['+capacity_type+']')
    fp.close()

def write_individual_cycle_file(x_list, x_name, y_list, y_name, filepath):
    header_comment_character = '#'
    delimiter = '\t'
    outfile = open(filepath, 'w')
    outfile.write(header_comment_character + x_name + delimiter + y_name + "\n")
    for x, y in zip(x_list, y_list):
        assert x != ""
        assert y != ""
        outfile.write(x + delimiter + y + "\n")
    outfile.close()

def write_individual_cycle_files(cycle_dict, capacity_type, path, filename_prefix):
    subfolder = os.path.join(path, 'individual_cycles')
    if not os.path.isdir(subfolder):
        os.mkdir(subfolder)
    for cycle_id in cycle_dict.keys():

        def write_cycle(cycle, step_type):
            filename = filename_prefix + "_" + step_type + str(cycle_id) + ".dat"
            filepath = os.path.join(subfolder, filename)
            write_individual_cycle_file(cycle[capacity_type], capacity_type, cycle['V'], 'V', filepath)

        try:
            this_cycle = cycle_dict[cycle_id]['charge']
            write_cycle(this_cycle, 'charge')
        except KeyError:
            logging.warning("No charge for cycle #{}".format(cycle_id))

        try:
            this_cycle = cycle_dict[cycle_id]['discharge']
            write_cycle(this_cycle, 'discharge')
        except KeyError:
            logging.warning("No discharge for cycle #{}".format(cycle_id))

def write_grace_input_file(cycle_dict, capacity_type, path, filename_prefix):
    filename = filename_prefix + "_grace_ascii.dat"
    filepath = os.path.join(path, filename)
    grace_input_file = open(filepath, 'w')
    delimiter = ' '
    record_separator = '\n'
    for cycle_id in cycle_dict.keys():
        def write_step(x_list, y_list, step_type):
            for x, y in zip(x_list, y_list):
                grace_input_file.write(x + delimiter + y + "\n")
            grace_input_file.write(record_separator)

        step_type = 'charge'
        try:
            write_step(cycle_dict[cycle_id][step_type][capacity_type], cycle_dict[cycle_id][step_type]['V'], step_type)
        except KeyError:
            logging.warning("No charge for cycle #{}".format(cycle_id))
        step_type = 'discharge'
        try:
            write_step(cycle_dict[cycle_id][step_type][capacity_type], cycle_dict[cycle_id][step_type]['V'], step_type)
        except KeyError:
            logging.warning("No discharge for cycle #{}".format(cycle_id))

    grace_input_file.close()

def write_gnuplot_input_file(cycle_dict, capacity_type, path, filename_prefix):
    filename = filename_prefix + "_plot.gnuplot"
    filepath = os.path.join(path, filename)
    gnuplot_input_file = open(filepath, 'w')
    header = """
    set xlabel "Capacity [{}]"
    set ylabel "Potential vs. Li/Li+ [V]"
    set title "{}"
    set key off
    set auto fix
    set style data points
    set yrange [0:*]
    """.format(capacity_type, filename_prefix)
    if os.name == 'nt':
        header += "set terminal wxt persist\n"
    else:
        header += "set terminal x11 persist\n"
    header += "plot '-' pointtype 0\n"
    gnuplot_input_file.write(header)
    for cycle_id in cycle_dict.keys():
        def write_step(x_list, y_list, step_type):
            for x, y in zip(x_list, y_list):
                gnuplot_input_file.write(x + ' ' + y + "\n")

        step_type = 'charge'
        try:
            write_step(cycle_dict[cycle_id][step_type][capacity_type], cycle_dict[cycle_id][step_type]['V'], step_type)
        except KeyError:
            logging.warning("No charge for cycle #{}".format(cycle_id))
        step_type = 'discharge'
        try:
            write_step(cycle_dict[cycle_id][step_type][capacity_type], cycle_dict[cycle_id][step_type]['V'], step_type)
        except KeyError:
            logging.warning("No discharge for cycle #{}".format(cycle_id))

    gnuplot_input_file.write("EOF\n")
    gnuplot_input_file.close()

def write_origin_input_file(cycle_dict, capacity_type, path, filename_prefix):
    filename = filename_prefix + "_origin_columnar.csv"
    filepath = os.path.join(path, filename)
    import csv
    origin_input_file = open(filepath, 'w')
    origin_csv = csv.writer(origin_input_file, delimiter=',')
    columns = []
    for cycle_id in cycle_dict.keys():
        for step_type in ['charge', 'discharge']:
            try:
                columns.append([step_type + '_' + str(cycle_id), capacity_type] + cycle_dict[cycle_id][step_type][capacity_type])
                columns.append([step_type + '_' + str(cycle_id), 'V'] + cycle_dict[cycle_id][step_type]['V'])
            except KeyError:
                #TODO: use warnings module to make these actual warnings.
                logging.warning("No {} for cycle #{}".format(step_type, cycle_id))
    # Now we need to turn the varying-length columns into rows so we can easily write them to a file.
    # https://muffinresearch.co.uk/python-transposing-lists-with-map-and-zip/
    rows = map(None, *columns)
    origin_csv.writerows(rows)
    origin_input_file.close()

def mass_from_user():
    def mass_mg_from_user():
        mass_mg = raw_input("Enter mass of active material in mg, or just press enter to calculate mAh: ")
        if mass_mg == "":
            return None
        elif float(mass_mg) == 0:
            print("Error: mass cannot be 0.")
            mass_mg_from_user()
        elif float(mass_mg) < 0:
            print("Error: mass cannot be negative.")
            mass_mg_from_user()
        else:
            return float(mass_mg)

    mass_mg = mass_mg_from_user()
    if mass_mg:
        mass_g = mass_mg / 1000.0
        require_mass_calculations = True
    else:
        mass_g = None
        require_mass_calculations = False
    return mass_g, require_mass_calculations

def main():
    require_mass_calculations = None
    if len(sys.argv) > 1:
        # Parse arguments and run non-interactively.
        parser = argparse.ArgumentParser(description='This is a script for processing data from a NEWARE battery cycler.')
        parser.add_argument('-m', '--mass', help='Mass in milligrams',required=False)
        parser.add_argument('-i', '--input', help='Input file',required=True)
        parser.add_argument('-v', '--verbose', action='store_const', dest='loglevel', const=logging.INFO, default=logging.WARNING)
        parser.add_argument
        args = parser.parse_args()
        logging.basicConfig(level=args.loglevel)
        input_file_path = args.input
        cycle_dict = parse_general_report(input_file_path)
        mass_g = infer_mass(cycle_dict)
        if args.mass:
            if mass_g:
                logging.warning("Mass inferred from file is {}mg but this is overriden by required value of {}mg".format(1000.0*mass_g, args.mass))
            require_mass_calculations = True
            mass_g = float(args.mass)/1000.0
        else:
            mass_g = infer_mass(cycle_dict)
            require_mass_calculations = False
    else:
        # Take interactive user input.
        while True:
            input_file_path = raw_input("Enter filename:")
            #TODO: make this more robust againt mistyped filenames.
            try:
                cycle_dict = parse_general_report(input_file_path)
                break
            except IOError:
                sys.stderr.write("No such file or directory:", input_file_path)

        mass_g = infer_mass(cycle_dict)
        if mass_g == None:
            mass_g, require_mass_calculations = mass_from_user()
        else:
            print("Mass is inferred to be {}mg".format(mass_g*1000))
            while True:
                yes_or_no = raw_input("Use this value for mass? ")
                try:
                    if distutils.util.strtobool(yes_or_no):
                        require_mass_calculations = False
                        break
                    else:
                        mass_g, require_mass_calculations = mass_from_user()
                        break
                except ValueError:
                    print("Please enter yes or no.")

    if require_mass_calculations:
        calculate_specific_capacities(cycle_dict, mass_g)
        capacity_type = 'mAh/g'
    else:
        capacity_type = 'mAh'

    input_file_path_no_extension = os.path.splitext(input_file_path)[0]
    basename_no_extension = os.path.splitext(os.path.basename(input_file_path))[0]
    out_dir = input_file_path_no_extension + "_data_extracted"
    logging.debug("Saving to folder {}".format(out_dir))
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    write_ini_file(input_file_path, cycle_dict, mass_g, out_dir, basename_no_extension)
    write_cycle_summary_file(cycle_dict, mass_g, out_dir, basename_no_extension)
    write_individual_cycle_files(cycle_dict, capacity_type, out_dir, basename_no_extension)
    write_grace_input_file(cycle_dict, capacity_type, out_dir, basename_no_extension)
    write_grace_cycle_summary(cycle_dict, capacity_type, out_dir, basename_no_extension)
    write_origin_input_file(cycle_dict, capacity_type, out_dir, basename_no_extension)
    write_gnuplot_input_file(cycle_dict, capacity_type, out_dir, basename_no_extension)

if __name__ == "__main__":
    main()
