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

try:
    with open(sat_lines_path, "r", encoding='utf8') as jf:
        sattelite_lines = json.load(jf)
except FileNotFoundError:
    print("no sat_lines.json file was found in the sub folder.\n"
          "the sat_lines.py should be executed to regerentate the json file.")

if __name__ == "__main__":
    import pandas as pd

    df = pd.read_excel(path.join(path.dirname(__file__),
                                 "sattelite_lines",
                                 'sattelite_lines.ods'),
                       dtype={"element": str, "designation": str,
                              "line": str, "sub": str,
                              "sup": str, "pos_str": str,
                              "Energy (eV)": str},
                       keep_default_na=False)
    df["html_str"] = df.designation
    df.html_str += df.line.where(
        df.line.values == "", '<i>' + df.line + '</i>', inplace=False)
    df["h_fp"] = df.html_str
    df["h_sup"] = df.sup.where(df.sup.isin(['′', '″', '‴', '⁗', '″,‴', '']),
                               '<sup>'+df.sup+'</sup>',
                               inplace=False)
    df.html_str += df.h_sup
    df["h_sub"] = df["sub"].where(
        df["sub"].values == "", '<sub>' + df["sub"] + '</sub>', inplace=False)
    df.html_str += df.h_sub
    df.html_str += df.post_str
    df["full_html_str"] = df.element + " " + df.html_str
    df["html_str_parted"] = df.element + ";" + df.h_fp + ";" + df.h_sup + ";" +\
        df.h_sub + ";" + df.post_str
    df["family"] = ""
    df.family.loc[df.designation.str.contains('M')] = "M"
    df.family.loc[df.designation.str.contains('K')] = "K"
    df.family.loc[df.designation.str.contains('L')] = "L"

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
