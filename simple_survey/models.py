from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'みなさんの名前を入れましょう．'

doc = """
簡単な調査アプリです．
"""

class Constants(BaseConstants):
    name_in_url = 'simple_survey'
    players_per_group = None
    num_rounds = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass
    
class Player(BasePlayer):
    name = models.StringField(verbose_name='あなたの名前を教えてください．')
    age = models.IntegerField(verbose_name='あなたの年齢を教えてください．')
    sex = models.CharField(initial=None,
                     choices=['男性', '女性', 'その他'],
                     verbose_name='あなたの性別を教えてください．',
                     widget=widgets.Select())
