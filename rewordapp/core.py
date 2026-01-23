# from typing import Any
# from rewordapp.deps import genericlib_Line as Line
#
#
# class RewordBuilder:
#     def __init__(self, txt: str):
#         self.txt = str(txt)
#
#         self.lines = (line for line in self.txt.splitlines(keepends=True))
#
#     @property
#     def raw_data(self):
#         return self.txt
#
#     def transform_line(self, line):
#         for token in line.do_finditer_split():
#             pass
#
#     def build(self):
#         result = []
#         for line in self.lines:
#             if line.is_optional_empty:
#                 result.append(line)
#             else:
#                 pass