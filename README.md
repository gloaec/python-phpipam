python-phpipam
==============

API written in python for phpipam

Installation instructions
-------------------------

1. Patch your existing setup of phpipam with contents from `patch/`
2. Setup API credentials in `phpipam.conf`
3. Use `./import` commandline utility

Usage
-----

    import -f <format> [-o <outputfile>]

        -f <format>     Possible values: ['csv','dhcpd.conf']
        -o <outpufile>  Import ouput file
