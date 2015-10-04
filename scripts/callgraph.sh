python -m cProfile -o profile.d wintersun/wintersun.py -d
gprof2dot -f pstats profile.d -o profile.dot
dot -Tpng profile.dot -o profile.png
