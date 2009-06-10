#!/usr/bin/python
"""
    Evanescent machine idle detection and shutdown tool.
    Copyright (C) 2008  James Shubin, McGill University
    Written for McGill University by James Shubin <purpleidea@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


"""this is the evanescent client that runs in the machines session"""

from idle.mouseidle import *
import evanescent.config



import pqueue				# my priority queue implementation
GGG.pq = pqueue.pqueue()		# initialize the priority queue

import clock				# my clock function
GGG.pq.put(clock.clock(ggg=GGG))	# run it as soon as possible

"""
sleep_until_idle(config.idle_time_limit)
if warned_user and not excluded:
	logmeoff()
"""

while True:

	m = mouseidle()
	if m < evanescent.config.IDLELIMIT:

		time.sleep(

	else:







while True:				# main loop

	peek = GGG.pq.peek()

	if peek == None:		# no events, so block and wait for file descriptor
		found = select.select(GGG.ins, GGG.outs, [])

	else:
		(item, datetime) = peek
		found = select.select(GGG.ins, GGG.outs, [], max(datetime - time.time(), 0) )



	# reading
	for obj in found[0]:		# if we have file descriptor classes that have returned, go through each of them
		obj.read()

	# writing
	for obj in found[1]:
		obj.write()


	ready = GGG.pq.ready()
	while ready > 0:
		(item, datetime) = GGG.pq.get()

		item.run()

		ready = ready - 1


print evanescent.config.IDLELIMIT
print mouseidle()
