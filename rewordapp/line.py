# import re
#
#
# class Line:
#     def __init__(self, line):
#         self._line = line
#         self._data = line.strip()
#         self._joiner = ""
#
#     @property
#     def raw_data(self):
#         return self._line
#
#     @property
#     def data(self):
#         return self._data
#
#     @property
#     def joiner(self):
#         if not self._joiner:
#             self._joiner = self._line[len(self._line.rstrip("\r\n")):]
#         return self._joiner
#
#
#
#
#
# def split_lines(txt):
#     for line in txt.splitlines(keepends=True):
#         pass
#
#
# def join_lines(lines):
#     result = []
#     for line in lines:
#         if isinstance(line, Line):
#             result.append(line)
#
