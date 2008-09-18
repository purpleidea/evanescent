SUBMITTED LATE WITH (SOME) PERMISSION. 

Professor Vybihal said that I can submit late (at a 10% penalty - the same as Thursday) if I attempt the two hardest problems. I couldn't get the windows installer working, unfortunately. However I did get some tray action coolness. (See: tray_icon.tar.gz)

+--------------+
| Website Team |
+--------------+

I worked alone, and I included the entire site in my submission. 

+---------------------+
| New Website Scripts |
+---------------------+

The scripts (buy.cgi and manage.pl) are under /cgi-bin/
The inventory (inventory.csv) is under /files/

My iventory is a weird format which is not quite space delimited or comma delimited! Since the entire catalogue is dynamically built from the inventory, the first few fields are comma delimited but the description field (the last field) is not.


+-----------------------+
|Building the .cgi files|
+-----------------------+

inventory.[ch] - Helps read and write to the inventory.
printPage.[ch] - Helps print a webPage given our template

buy.cgi requires: printPage.h printPage.c inventory.h inventory.c buy.h buy.c

catalogue.cgi requires: printPage.h printPage.c inventory.h inventory.c catalogue.h catalogue.c

login.cgi requires: printPage.h printPage.c login.h login.c

+--------------+
|User Accounts |
+--------------+

There are currently two accounts that you can use when logging in:

A regular user account: User/Pass
An administrator account: Rob/Rolnick

The regular user does not see any special functionality when logged in, but the administrator can modify the inventory.

+---------------+
| Cool Features |
+---------------+

The catalogue is dynamically built from the inventory, adding and removing objects to the inventory will also change the catalogue. Items that are sold out do not get displayed. 

If you buy a greater quantity of some items than is currently in stock, you are only billed for the amount that can be shipped.

In addition to adding/removing items to the inventory, you can also replenish the stock of each item from the administration page

+-------+
| Notes |
+-------+

The catalog has a few extra fields than is strictly required. These are the fields for the item name (which is not guaranteed to be unique), its description, and the extension on the image for the product. 

Although there is no way of adding images without FTP access, you can specify the extension that the picture would have. Even so, an "image unavailable" picture should be placed in its place.

+------------+
| Evanescent |
+------------+

I implemented the tray icon, without doing the file signalling (wasn't sure how that worked, and I figured I put in enough work after fighting with call backs and threading issues!

Turns out pynotify's examples don't all work due to call back issues. (Try: /usr/share/doc/python-notify/examples/test-xy-stress.py) The callback never happens!

Also, pygtk won't render the gui unless you make a blocking call. Having the whole application pause to show a tray icon, was obviously a very bad idea. So I chose to compromise. The tray icon is only visible when there is a notification, and at that time the application is blocked. Looking into threading would be a good idea, though, I suppose.
