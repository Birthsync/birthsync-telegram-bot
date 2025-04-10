from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from config.config_reader import settings

chat = GigaChat(credentials=settings.CREDENTIALS,
                verify_ssl_certs=False,
                model='GigaChat-2-Max')


async def ai_gifts_generator(data):

    fio = data.get('fio')
    birthdate = data.get('birthdate')
    categories = data.get('categories')

    prompt = f'Персона: {fio}; Дата рождения: {birthdate}; Категории: {categories}'

    messages = [SystemMessage(content=("Ты — ассистент по генерации подарков. "
                                       "На основе переданных категорий и их содержимого ты должен сгенерировать ровно 10 разных хороших и интересных подарков, "
                                       "релевантных этим данным, которые существуют в реальности. "
                                       "Пиши каждый подарок с новой строки, с нумерацией. "
                                       "Никаких комментариев, пояснений или лишнего текста — только список из 10 уникальных подарков."
                                       "Не советуй ничего негативного и что может быть связано со здоровьем.")),
                HumanMessage(content=prompt)]
    res = await chat.ainvoke(messages)

    print(res.content, res.response_metadata.get)

    return res.content
