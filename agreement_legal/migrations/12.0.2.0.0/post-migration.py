# Copyright (C) 2020 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(env, version):
    if not version:
        return

    env.execute("UPDATE agreement_stage SET stage_type = 'agreement' "
                "WHERE stage_type IS NULL;")
