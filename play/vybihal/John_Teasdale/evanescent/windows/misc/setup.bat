REM    Evanescent machine idle detection and shutdown tool.
REM    Copyright (C) 2008  James Shubin, McGill University
REM    Written for McGill University by James Shubin <purpleidea@gmail.com>
REM
REM    This program is free software: you can redistribute it and/or modify
REM    it under the terms of the GNU Affero General Public License as published by
REM    the Free Software Foundation, either version 3 of the License, or
REM    (at your option) any later version.
REM
REM    This program is distributed in the hope that it will be useful,
REM    but WITHOUT ANY WARRANTY; without even the implied warranty of
REM    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM    GNU Affero General Public License for more details.
REM
REM    You should have received a copy of the GNU Affero General Public License
REM    along with this program.  If not, see <http://www.gnu.org/licenses/>.

REM ** this script is used to create a Python .exe
@echo off

REM ** go to the correct directory
C:
cd C:\James\evanescent\

REM ** get rid of all the old files in the build folder
rd /S /Q build

REM ** get rid of all the old files in the dist folder
rd /S /Q dist

REM ** create the exe
C:\Python25\python.exe setup.py py2exe

REM ** pause so we can see the exit codes
pause "done...hit a key to exit"
