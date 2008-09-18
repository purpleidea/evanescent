ASSIGNMENT 5 - INTRO TO SOFTWARE SYSTEMS - README

Alexandre Boyer Laporte (260329867)
Andrew Sutcliffe (260323075)
Francis Brassard (260322731)

We have not received a team ID at all and it's been what 4 wrrks, so we just worked together, without RCS.

PART ONE - WEB DEV.

To compile the submitWebsite.cgi (it will automatically compile the buy.c)

====> gcc -o submitWebsite.cgi submitWebsite.c buy.c -lm

-lm added for the math library


Login username is "jesus"
Login password is "christ"

If you add an item, make sure you format the price with a dot "." and not a comma ",".
The PST is calculated over the GST, as it is done in real life.
The way "List items" has been done is weak, we know, it required Javascript to be enabled, but it still does work.

PART TWO - PYTHON DEV.

Evanescent ( python ):


We chose to implement the date exclusion. At first we slightly
misinterpreted the way the program  worked, which led us to implement
a field which allowed the user to input multiple co-dependant time and
date periods. This was later deemed useless by James since the format
was more complex and the user could just choose to use multiple entries.
While we would argue our syntax wasn't much more complex, and it
provided the possibility of providing multiple time periods within
one exclusion block, thus limiting the making of multiple blocks while
changing only the time and date fields, we decided to upgrade our
implementation in order to support day names in string format(Monday,...).
While this modification reflects on the code of the is_date function
we decided to leave the field tmdt there so that one could enter a time,
a date and a day period. In doing so we allow the user to enter the time
restrictions under our more advanced format if he chooses to do so, while 
the normal user can still use the old format but now he has the added 
option to exclude certain weekdays. 

advanced string format :

time1/date1;time2;/date3

where time it [hh:mm:ss,hh:mm:ss]
and date is   [dd:mm:yyyy,dd:mm:yyyy] or [dayoftheweek,dayoftheweek]

supports single date (only that day) and time (until the next hour)
entries, as well as date wrap arounds(december 25 to january 1st
or saturday to tuesday) and also the follwing dd dd:mm hh hh:mm 