"""
Sample models
"""

from app.orm.models import Session, User, Lang, Phrase, Phrasebook, PhrasebookPhrase, Consumer
from app.rest.auth_api import gen_token, password_hash


def sample_data():
    """
    creates sample data
    """
    session = Session()

    lang1 = Lang()
    lang1.key = 'en'
    lang1.codes = ' en en_UK en_US English english eng '
    session.add(lang1)

    lang2 = Lang()
    lang2.key = 'ru'
    lang2.codes = ' ru ru_Ru Russion russion rus '
    session.add(lang2)

    phrase1 = Phrase()
    phrase1.gen_id()
    phrase1.text1 = 'phrase 1'
    phrase1.text2 = 'trans 1'
    phrase1.lang1 = lang1.key
    phrase1.lang2 = lang1.key
    session.add(phrase1)

    phrase2 = Phrase()
    phrase2.gen_id()
    phrase2.text1 = 'phrase 2'
    phrase2.text2 = 'rus trans 2'
    phrase2.lang1 = lang1.key
    phrase2.lang2 = lang2.key
    session.add(phrase2)

    users1 = User()
    users1.gen_id()
    users1.email = 'brooth@gmail.com'
    users1.password = password_hash('123')
    users1.name = 'Oleg Kh'
    session.add(users1)

    phrasebook1 = Phrasebook()
    phrasebook1.gen_id()
    phrasebook1.user_id = users1.id
    phrasebook1.name = 'Test Phrasebook'
    session.add(phrasebook1)

    pp1 = PhrasebookPhrase()
    pp1.gen_id()
    pp1.phrasebook_id = phrasebook1.id
    pp1.phrase_id = phrase1.id
    session.add(pp1)

    pp2 = PhrasebookPhrase()
    pp2.gen_id()
    pp2.phrasebook_id = phrasebook1.id
    pp2.phrase_id = phrase2.id
    session.add(pp2)

    consumer1 = Consumer()
    consumer1.gen_id()
    consumer1.user_id = users1.id
    consumer1.secret = gen_token()
    consumer1.name = 'Test Consumer'
    session.add(consumer1)

    session.commit()
