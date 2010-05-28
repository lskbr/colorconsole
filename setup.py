#!/usr/bin/env python
#
#    colorconsole
#    Copyright (C) 2010 Nilo Menezes
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from distutils.core import setup

setup(name='colorconsole',
      version='0.5',
      description = "Simple console routines to enable colors and cursor positioning.",
      author='Nilo Menezes',
      author_email='nilo@nilo.pro.br',
      url='http://code.google.com/p/colorconsole/',
      packages=['colorconsole'],
      license = "LGPL",
      scripts=[],    
      long_description = 
      """
colorconsole uses a common set of console (text mode) primitives, available on Windows, Linux and Mac OS X.
The API is the same on all operating systems and applications should run without modifications on any of them.
The Windows API or ANSI scape codes are used depending on the platform.
This library is licensed under the terms of the GNU LGPL.
""",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',          
      ] ,
      
     )

