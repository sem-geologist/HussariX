"""Non-diagram (sattelite) lines based on Cachois and Senemaud 1978;
As notation used in the book is not very consistent, conversion into IUPAC form
would be not clear, thus notation is left as is.
Dictionary is generated and cached in sat_lines.json from ods file;
As it is intended to be used in UI, and plain html would have ugly form of
<sup> and <sub> misalignment, dictionary contains blocks of html for piece by
piece painting at right positions (with Qt).

##References:##
* Cauchois Y., Senemaud C. 1978,
  Wavelengths of X-ray emission lines and absorption edges.
  Pergamon Press, Oxford, New York, Toronto, Sydney, Paris, Frankfurt"""

import json
from os import path

__all__ = ['sattelite_lines']

sat_lines_path = path.join(path.dirname(__file__),
                           "sattelite_lines",
                           "sat_lines.json")

DEBUG = True

try:
    with open(sat_lines_path, "r", encoding='utf8') as jf:
        sattelite_lines = json.load(jf)
except FileNotFoundError:
    print("no sat_lines.json file was found in the sub folder.\n"
          "the sat_lines.py should be executed to regerentate the json file.")

if __name__ == "__main__":
    import pandas as pd
    import numpy as np

    df = pd.read_excel(path.join(path.dirname(__file__),
                                 "sattelite_lines",
                                 'sattelite_lines.ods'),
                       dtype={"element": str, "designation": str,
                              "line": str, "sub": str,
                              "sup": str, "pos_str": str,
                              "Energy (eV)": np.float64},
                       keep_default_na=False)
    if DEBUG: 
        print(df.sup.unique())
        print(df["sub"].unique())
    df["html_str"] = df.designation
    df["weight"] = 0.05
    df.html_str += df.line.where(
        df.line.values == "", '<i>' + df.line + '</i>', inplace=False)
    df["h_fp"] = df.html_str
    df["h_sup"] = df.sup.where(df.sup.isin(['′', '″', '‴', '⁗', '″,‴', '']),
                               '<sup>'+df.sup+'</sup>',
                               inplace=False)
    df.loc[df["sup"].str.contains('′'), "weight"] = df[df["sup"].str.contains('′')]["weight"] / 6
    df.loc[df["sup"].str.contains('″'), "weight"] = df[df["sup"].str.contains('″')]["weight"] / 9
    df.loc[df["sup"].str.contains('‴'), "weight"] = df[df["sup"].str.contains('‴')]["weight"] / 12
    df.loc[df["sup"].str.contains('⁗'), "weight"] = df[df["sup"].str.contains('⁗')]["weight"] / 15
    df.loc[df["sup"].str.contains('″,‴'), "weight"] = df[df["sup"].str.contains('″,‴')]["weight"] * 10 
    df.loc[df["sub"].str.isnumeric(), "weight"] = df[df["sub"].str.isnumeric()]['weight'] / (df[df["sub"].str.isnumeric()]["sub"].astype(float) + 1)
    df.loc[df["sub"].str.isnumeric() & df["sup"].str.len() == 0, "weight"] *= 15
    df.loc[df["sup"].str.isalpha(), "weight"] = df[df["sup"].str.isalpha()]['weight'] / 8
    df.loc[df["sub"].str.isalpha(), "weight"] = df[df["sub"].str.isalpha()]['weight'] / 8
    df.loc[df["sub"].str.startswith("0"), "weight"] = df[df["sub"].str.startswith("0")]["weight"] / 12
    df.html_str += df.h_sup
    df["h_sub"] = df["sub"].where(
        df["sub"].values == "", '<sub>' + df["sub"] + '</sub>', inplace=False)
    df.html_str += df.h_sub
    df.html_str += df.post_str
    df["full_html_str"] = df.element + " " + df.html_str
    df["html_str_parted"] = df.element + ";" + df.h_fp + ";" + df.h_sup + ";" +\
        df.h_sub + ";" + df.post_str
    df["family"] = ""
    df.loc[df.designation.str.contains('M'), "family"] = "M"
    df.loc[df.designation.str.contains('K'), "family"] = "K"
    df.loc[df.designation.str.contains('L'), "family"] = "L"
    df.loc[df.designation.str.contains('N'), "family"] = "N"
    df.loc[df["weight"] > 0.2, "weight"] /= 10
    if DEBUG:
        print(df["family"].unique())
        print(df["weight"].min())
        print(df["weight"].max())
        import matplotlib.pyplot as plt
        ax = df.weight.hist()
        plt.show()
    # as we have html (sub-)strings we don't need these in dictionary:
    df.drop(columns=["designation", 'line', 'sub', 'sup', 'post_str', 'h_sub',
                     'h_sup', 'h_fp', 'html_str'],
            inplace=True)
    # sanitize name:
    df.rename({'Energy (eV)': "energy"}, axis=1, inplace=True)
    print(df.columns)

    # lets make a dictionary:
    sat_d = df.to_dict('records')

    # rearange it to a more usable form for easier selection by element:
    new_d = {}
    for i in sat_d:
        key = i['element']
        if i['element'] not in new_d:
            new_d[key] = []
        del i['element']
        new_d[key].append(i)

    # overwrite the json file:
    print("making new sat_lines.json file")
    with open(sat_lines_path, 'w', encoding='utf8') as jf:
        json.dump(new_d, jf, ensure_ascii=False, indent=2)
