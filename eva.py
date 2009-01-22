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

# THIS SHOULD BE A CLIENT THAT RUNS ON USER LOGIN.
# IT SHOULD WRITE THE USERNAME AND IDLE TIME TO A
# COMMON FOLDER UNDER A UNIQUE NAME
# eg: common_folder/username
# AND THE MAIN EVANESCENT JOB SHOULD POLL THAT AND
# INCLUDE THOSE IN IT'S SEARCH FOR GETTING DATA FOR
# THE __WIDLE() FUNCTION. THIS MAIN DAEMON/JOB WOULD
# ALSO WRITE STATUS BUBBLE MESSAGES TO A COMMON FILE
# eg: common_folder_msg/username WHERE THE EVA CLIENT
# (WHICH IS THIS PROGRAM, WILL POLL OR SELECT FROM
# AND THEN DISPLAY TO THE CLIENT.)
# MAYBE WE CAN GET SOME SORT OF IPC PYTHON THING GOING
# INSTEAD OF PASSING THROUGH FILES. MAYBE NOT. WHO KNOWS.

