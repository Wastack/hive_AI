import pstats
import os

__location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
p = pstats.Stats(os.path.join(__location__,'result.out'))

p.sort_stats('cumulative').print_stats(30)