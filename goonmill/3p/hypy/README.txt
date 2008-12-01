## $Id: README.txt,v 1.7 2007/04/17 12:40:02 yosida Exp $

Native Python Binding of Hyper Estraier

* Overview
This is an implementation of Python binding for ``Core API'' of Hyper
Estraier. This is developed on these environment :
 - hyperestraier-1.4.8
 - qdbm-1.8.74
 - Linux 2.4.31, Linux 2.6.9
 - Python 2.4.2

* Install
 % python setup.py build
 % sudo python setup.py install

* Usage 
See examples/*.py and ``core API'' interface in estraier.idl
See also rubynative/estraier-doc.rb . 
... and read source code (sorry).

I refer to the interface of Document, Database, Condition, and
Result in estraier-doc.rb

* License

Native Python Binding of Hyper Estraier
Copyright (c) 2007 SOUNDBOARD Co.,Ltd. 

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


