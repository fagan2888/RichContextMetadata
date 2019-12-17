import unittest
import sys
from glob import glob
from pathlib import Path
import codecs
import csv 
import os 

csv_paths = []

# TODO: please add to this list more bad encodings when found
bad_unicodes = ["â€™", "‚Äô", "‚Äò", "‚Äú", "‚Äù", "‚Äì", "â€œ"]

class TestSample(unittest.TestCase):

    def test_correct_num_to_test(self):
        self.assertTrue(len(csv_paths) > 0, "No files to be checked, please check used arguments.")

    def test_contains_unicode(self):
        badlyEncodedFiles = {}
        exception_count = 0
        for csvpath in csv_paths:
            try: 
                with codecs.open(csvpath, encoding="UTF-8") as f:
                    csv_reader = csv.reader(f, delimiter=",")
                    for row in csv_reader:
                        for badUnicode in bad_unicodes: 
                            if any(badUnicode in field for field in row):
                                path, filename = os.path.split(csvpath)
                                badlyEncodedFiles.setdefault(filename,set()).add(badUnicode)
            except Exception as e: 
                print(e)
                print("Issue opening: {}".format(csvpath))   
                exception_count += 1

        print("{} Files threw exceptions when opening".format(exception_count))
        print("Files with bad unicode characters:")
        for key in badlyEncodedFiles:
            print(key, badlyEncodedFiles[key])

        self.assertTrue(len(badlyEncodedFiles) == 0, "{} Files are not properly encoded".format(len(badlyEncodedFiles)))

if __name__ == '__main__':
    metadata_dir_path = os.path.dirname(os.path.abspath(__file__)) + "/../metadata"
    print(sys.argv)
    if len(sys.argv) == 1:
        csv_wild_path = "/*/*.csv"
        print("Checking Metadata Files In: {}".format(metadata_dir_path + csv_wild_path))
        for csvpath in glob(metadata_dir_path + csv_wild_path):
            csv_paths.append(csvpath)
    elif len(sys.argv) == 2:
        filename = sys.argv.pop()
        path = metadata_dir_path + '/*/' + filename
        print("Checking Metadata File(s) In: {}".format(path))
        for csvpath in glob(path):
            print(csvpath)
            csv_paths.append(csvpath)

    print("Files to check: {}".format(len(csv_paths)))
    unittest.main()