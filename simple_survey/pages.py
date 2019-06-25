from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

class Page1(Page):
    form_model = 'player'
    form_fields = ['name', 'age', 'sex']

class Page2(Page):
    pass

page_sequence = [
    Page1,
    Page2
]
