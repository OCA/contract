# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def _default_sequence(self):
    maxrec = self.search([], order='sequence desc', limit=1)
    if maxrec:
        return maxrec.sequence + 10
    else:
        return 0
