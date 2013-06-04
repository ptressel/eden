# -*- coding: utf-8 -*-
"""
Integrate translations supplied as csv with existing language .py file.

NOTE: This was written for Google Code-In (GCI) 2011, so may contain some
quirks specific to how translations were provided for that event.

Input is a file that specifies the paths of the current language .py file
and the csv files for the same language.  Supply the path to this file
on the command line.  Format of the input file is:

py_file = "path/to/language.py"
csv_files = ["path/to/first.csv", "path/to/second.csv",...]

If there is no current language .py file, supply instead the untranslated
(US-English) .py file.

Each input csv file is expected to be in UTF-8 encoding, to have one line
of heading (with heading text "location","source","target" case-insensitive),
and to have three columns: the first is ignored, second is the key string,
and third is the translation.

This script does the following:

Keeps any translations already in the language .py file, under the assumption
that these were produced under more controlled circumstances, and are known
to be acceptable.  Note the existence of a translated string is assumed when
the key string != the value string.

Checks that each csv file is UTF-8, reports and does not use any that are not
UTF-8.

For each line in each UTF-8 csv file:

Reads the key and translation strings out of the csv.

If the key is in the current language .py file and has a translation, the
new translation is not used for the output .py file, but is saved along with
the original translation in a file of alternate translations, for later
review.

Clips leading and trailing spaces, as some csv files were observed to contain
such.  Note if the string incorporates all variable values through formats,
it probably does not need either leading or trailing spaces.  Translations
with leading or trailing spaces are used but reported.

Checks for the existence of the same set of Python format specifiers in both
key and translated strings.  (That is, if the original key string contains
%(thing)s and %(stuff)s, so must the translation, but the order may differ.)
Translations with a mismatch in format specifiers are reported and not used.

Surviving translations are added to the output language .py file.

After all files are processed, any keys lacking translations are added back in
to the output language .py file.

Several files are written to the current directory -- all file names start
with the language abbreviation from the name of the input language .py file
(say this is xx).  Output files are:

xx_new.py -- the composite language .py file.

xx_errors.list -- csv files that failed a UTF-8 check, had an incorrect
heading or wrong number of columns, or had other issues that might cause the
file to be interpreted incorrectly.  Each file name is followed by an error
message.  Most of the problems called out here can likely be repaired without
knowledge of the target language.

xx_warnings.list -- csv files that had non-fatal issues such as less than
90% translated strings.  These files were used in the integrated set.

xx_alternatives.csv -- alternative translations for the same key string.
Format is a comma-separated file with the key string, any translation from
the original language .py file, then any translations from csv files.

xx_spaces.csv -- any lines in which the translation had leading or trailing
spaces.  Format is key, translation, csv file path, line number (1-based,
as per usage in spreadsheets and editors).

xx_bad_formats.csv -- any lines in which the set of Python formats in the
key string do not match those in the translation, independent of order.
Format is key, translation, csv file path, line number (1-based, as per
usage in spreadsheets and editors).
"""

import sys, re, codecs, csv

# Parameters that might change or be unnecessary post-GCI.
max_pct_missing = 10.
key_heading = "source".lower()
val_heading = "target".lower()

# Use the script docstring as usage message.
usage = globals()["__doc__"]

# A somewhat simplified regex pattern for string format specifiers:
# doesn't attempt to exclude (e.g.) precision on an s conversion.
# Almost worked the first time -- forgot the + on the mapping key. ;-)
format_pattern = r"(%(?:\([\w" + r'"' + r"'-]+\))?[#0 +-]*(?:\*|(?:\d+(?:\.\d+)?))*[hlL]*[cdeEfFgGiorsuxX])"

def extract_formats(text):
    formats = re.findall(format_pattern, text)
    return formats.sort()

def errmsg(message, usage=usage, die=True):
    if message:
        print >> sys.stderr, message
	if usage:
	    print >> sys.stderr, usage
    if die:
        sys.exit(1)

def process_translations(usage, outfile, py_file, csv_files):
    # Load the .py file and separate it into translated and untranslated
	# strings.  The .py file contains a dict, not an assignment whose
	# value is a dict, so we can't just import it.  One presumes, since
	# we've been requiring UTF-8, that our .py files don't violate that.
	# Read it in as a string and assign it to something.
	try:
	    py_text = codecs.open(py_file, "r", "utf-8").read()
    except:
	    errmsg("Unable to read %s" % py_file)
	try:
	    # If this gives any trouble (e.g. with encodings) can use web2py's
		# functions for reading these files in gluon/languages.py.
	    current = exec(py_text)
    except:
	    errmsg("Unable to extract dict from %s" % py_file)
    current_trans = {}
    current_untrans = {}
    for key, val in current.iteritems():
        if key == val:
            current_untrans[key] = val
        else:
            current_trans[key] = val
    # Copy that in as the initial set of translations for the output file.
    integrated = dict(current_trans)

    errors = []
    warnings = []
    spaces = []
    bad_formats = []
    alternatives = {}

    # Check that each csv file is UTF-8, then process its translations.
    # Note: Although we open the file using codecs.open, the resulting
    # reader isn't directly useful for the csv module. Since that works
    # just fine for UTF-8 files with the built-in open, don't bother
    # jumping through hoops to reuse the codecs reader.
    # If there is need to process Unicode files, see:
    # http://docs.python.org/library/csv.html#examples
    for csv_file in csv_files:
        try:
            f = codecs.open(csv_file, "r", "utf-8")
            f.read()
            f.close()
        except:
            errmsg("File %s is not UTF-8, skipping." % csv_file, "", False)
            errors.append([csv_file, "File is not UTF-8"])
            continue
        
        with open(csv_file, "rb") as f:
            r = csv.reader(f)
            nrows = 0
            nmissing = 0

            row = r.next()  # read heading row
            if len(row) != 3 \
               or row[1].lower() != key_heading or \
               row[2].lower() != val_heading:
                errors.append([csv_file, "Column headings not as expected"])
                continue
            
            for row in r:
                if len(row) != 3:
                    errors.append([csv_file, "Row with len != 3 found"])
                    break
                nrows = nrows + 1
                key = row[1].strip()
                val_raw = row[2]

                # Strip leading & trailing spaces from the translation.
                # (Won't report presence of spaces unless the line passes the
                # next several checks.)
                val = val_raw.strip()

                # If the value is blank or same as the key, skip it.
                # These aren't errors, but we do report files with more than
                # the specified max percent missing.
                if not val or key == val:
                    nmissing = nmissing + 1
                    continue

                # Do the same set of format specifiers occur in key and
                # translation?
                key_formats = extract_formats(key)
                val_formats = extract_formats(val)
                if key_formats != val_formats:
                    bad_formats.append([key, val, csv_file, nrows])

                # Were there leading or trailing spaces on the translation?
                if val != raw_val:
                    spaces.append([key, val, csv_file, nrows])

                # Is there already a translation for this key?
                int = integrated.get(key, "")
                if int:
                    # Yes.  Already have some alternatives for this key?
                    alts = alternatives.get(key, [])
                    if not alts:
                        # None yet -- start alternatives list with the key.
                        alts.append(key)
                        # Next add the current translation if there was one,
                        # else include a blank so the reviewer knows whether
                        # the alternatives were all from this set of csv files.
                        curr = current_trans.get(key, "")
                        alts.append(curr)
                        # If there wasn't a current translation, then what's in
                        # the integrated set must be from these csv files too.
                        alts.append(int)
                    alts.append(val)
                else:
                    # Survived the checks and no prior translation -- use it.
                    integrated[key] = val

            else:
                # Finished that file normally -- check fraction translated.
                missing_pct = missing * 100. / nrows
                if missing_pct > max_missing_pct:
                    warnings.append([csv_file, "%f%% strings lack translations" % missing_pct])

if __name__ == "__main__":
    # Usage is described above. Briefly:
    #   python integrate_csv_translations.py input-path output-path
    # where input-path points to the file of arguments described in the
	# script docstring, and output-path is where the combined language .py
	# file should be written.
	args = sys.argv
	nargs = len(sys.argv) - 1

    if nargs < 2 or nargs >= 1 and args[1] == "--help":
	    errmsg("")

    argfile_str = sys.argv[1]
	try:
        exec "from %s import py_file, csv_files"
	except ImportError:
	    errmsg("Unable to import py_file and csv_files from %s" % argfile_str)
	
    outfile_str = args[2]
    try:
        outfile = open(outfile_str, mode="w")
    except:
        errmsg("Unable to write to %s" % outfile_str)

	process_translations(usage, outfile, py_file, csv_files)

    outfile.close()
    sys.exit(0)