# Core oTree/Django imports
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
# Additional Django utility for DB-level atomic operations
from django.db import transaction


author = 'あなたの名前を入力してください．'

doc = """
公共財ゲームです．
"""


class Constants(BaseConstants):
    name_in_url = 'public_goods_trial'
    players_per_group = 4
    num_rounds = 1

    endowment = c(100)
    multiplier = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()

    @transaction.atomic
    def compute(self):
        """Aggregate contributions and distribute individual payoffs.

        Wrapped in `transaction.atomic` to guard against race-conditions if the
        application scales to larger groups or concurrent requests.
        The players list is retrieved only once to avoid redundant DB hits.
        """
        players = list(self.get_players())  # single DB query

        # Calculate the group's total contribution in Python memory; negligible
        # cost for small groups but O(n) rather than O(2n) thanks to single loop
        total = sum(p.contribution for p in players)

        self.total_contribution = total
        self.individual_share = total * Constants.multiplier / Constants.players_per_group

        # Vectorised payoff computation within the same transaction
        for p in players:
            p.payoff = Constants.endowment - p.contribution + self.individual_share


class Player(BasePlayer):
    contribution = models.CurrencyField(
        choices=currency_range(c(0), c(Constants.endowment), c(1)),
        label="あなたはいくら貢献しますか？",
        widget=widgets.Slider()
    )
