#!/usr/bin/python
import sys
import getopt

def dump(args=[], opt_str = ''):
    """
    dump args like: ./dump_argvs.py -n eli -u root -p 123456
    return a dictionary
    opt_str like: h-help,n-name:,u-user:,p-password:
    "n" for short, "name" for long, ":" for with parameter
    """
    if not len(args) or not opt_str or not len(opt_str):
       return

    # dump short and long opt
    short_opt = ''
    long_opt = []
    for combind in opt_str.split(','):
       items = combind.split('-')
       if len(items) != 2:
         break
       have_extra = ':' in items[1]

       _short = items[0] + (':' if have_extra else '')
       _long = items[1].replace(':', '=')

       short_opt += _short
       long_opt.append(_long)
    # empty
    if not (len(short_opt) and len(long_opt)):
       return

    # dump options
    opts = None
    try:
       opts, argvs = getopt.getopt(args, short_opt, long_opt)
    except Exception as e:
       print('dump ', e)

    if opts:
       result={}
       for opt, arg in opts:
         result[opt] = arg
       return result
    pass

if __name__ == '__main__':

    rst = dump(sys.argv[1:], 'h-help,n-name:,u-user:,p-password:')
    print(rst)
