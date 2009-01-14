'    Evanescent machine idle detection and shutdown tool.
'    Copyright (C) 2008  James Shubin, McGill University
'    Written for McGill University by James Shubin <purpleidea@gmail.com>
'
'    This program is free software: you can redistribute it and/or modify
'    it under the terms of the GNU Affero General Public License as published by
'    the Free Software Foundation, either version 3 of the License, or
'    (at your option) any later version.
'
'    This program is distributed in the hope that it will be useful,
'    but WITHOUT ANY WARRANTY; without even the implied warranty of
'    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
'    GNU Affero General Public License for more details.
'
'    You should have received a copy of the GNU Affero General Public License
'    along with this program.  If not, see <http://www.gnu.org/licenses/>.

' dll from: http://dev.remotenetworktechnology.com/wsh/comwsh.htm

' this won't work until you've done: "regsvr32 p_GetLastInput.dll" first
Set obj = CreateObject("p_GetLastInput.clsIdle")
WScript.Echo "WIDLE"
WScript.Echo obj.IdleTime

