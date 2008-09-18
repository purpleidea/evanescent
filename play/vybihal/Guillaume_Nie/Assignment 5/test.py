#!/usr/bin/python
# TEST FILE
import datetime
import dt
import exclusions


print
print("Now, some tests will be conducted to check to see if dt.py works.")
print("Format: 4 tests - The two first shall write PASS if the function returns ")
print("\tTrue, and the 2 last ones shall write PASS id the function returns")
print("\tFalse. PASS indicates that the test followed expectations, and FAIL")
print("\tindicates otherwise. Please remove everything after \"\"\"TEST\"\"\"")
print("\tafterwards.")
print("Thank you.")
print
a=dt.dt()
print("Four tests for is_time:")
print("20:20")
if dt.dt.is_time(a,"20:20"):
    print("\tPASS")
else:
    print("\tFAIL")
print("20")
if dt.dt.is_time(a,"20"):
    print("\tPASS")
else:
    print("\tFAIL")
print("1:00")
if dt.dt.is_time(a,"1:00"):
    print("\tFAIL")
else:
    print("\tPASS")
print("1:00,2:00")
if dt.dt.is_time(a,"1:00,2:00"):
    print("\tFAIL")
else:
    print("\tPASS")
print
print("Four tests for is_date:")
print("25-05-1900,25-05-2500")
if dt.dt.is_date(a,"25-05-1900,25-05-2500"):
    print("\tPASS")
else:
    print("\tFAIL")
print("25-05-2500")
if dt.dt.is_date(a,"25-05-2500"):
    print("\tPASS")
else:
    print("\tFAIL")
print("25-05-1900")
if dt.dt.is_date(a,"25-05-1900"):
    print("\tFAIL")
else:
    print("\tPASS")
print("25-05-1900,25-05-1910")
if dt.dt.is_date(a,"25-05-1900,25-05-1910"):
    print("\tFAIL")
else:
    print("\tPASS")


print
print("Now, some tests will be conducted to check to see if this exclusions.py works.")
print("Format: 1 test - PASS if the function returns True, and FAIL otherwise.")
print
print("Exclusions test:")
b=exclusions.exclusions("evanescent.conf.yaml.example")
print("bob as a user")
if b.is_excluded("bob"):
	print("\tPASS")
else:
	print("\tFAIL")
print
