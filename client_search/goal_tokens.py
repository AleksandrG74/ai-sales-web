"""
Токены цели — маркеры согласия клиента в диалоге.
Используются для поиска успешных диалогов и PMI-оценки.
"""

import re
from typing import List, Set, Dict


# ─── Нормализация ─────────────────────────────────────────────────
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Нижний регистр, ё→е, удаление пунктуации, сжатие пробелов."""
    if not text:
        return ""
    text = text.lower().replace("ё", "е")
    text = _PUNCT_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    return text


# ─── Группы токенов согласия ──────────────────────────────────────

DIRECT = [
    "да", "ага", "угу", "окей", "ок", "хорошо", "ладно",
    "договорились", "согласен", "согласна", "согласны",
    "принимаю", "соглашусь", "подходит", "устраивает",
]

ACTION = [
    "беру", "возьму", "заказываю", "закажу", "оформляю", "оформлю",
    "покупаю", "куплю", "оплачиваю", "оплачу",
    "поехали", "давайте", "давай", "начинаем", "погнали",
]

CHOICE = [
    "это то что нужно", "то что надо", "как раз то",
    "идеально", "отлично", "супер", "класс",
    "годится", "выбираю это", "останавливаюсь на этом",
]

CONDITIONS = [
    "по рукам", "по цене согласен", "цена устраивает",
    "меня устраивает цена", "условия подходят", "сроки подходят",
    "доставка подходит", "все устраивает", "все подходит",
]

READINESS = [
    "как оплатить", "куда платить", "как заказать", "как оформить",
    "какие реквизиты", "дайте ссылку", "скиньте ссылку",
    "пришлите ссылку", "как связаться",
    "готов", "готов оформлять", "готов оплачивать", "готов к сделке",
]

FINAL = [
    "давайте оформим", "давайте закажем", "давайте начнем",
    "приступайте", "оформляйте", "заказывайте",
    "высылайте", "отправляйте счет", "выставляйте счет",
    "заключаем", "договорились окончательно",
    "беру этот", "беру его",
]

EMOTIONAL = [
    "вау круто беру", "о да", "конечно", "еще бы",
    "само собой", "разумеется", "безусловно",
    "на все сто", "стопроцентно", "однозначно да",
]

CONDITIONAL = [
    "да но", "да только", "согласен но", "хорошо если",
    "ладно если", "беру если", "готов если", "подходит если",
]

POLITE = [
    "спасибо беру", "благодарю согласен",
    "спасибо оформляйте", "благодарю за предложение согласен",
    "спасибо устраивает",
]


# ─── Токены цели (25 главных для PMI) ─────────────────────────────
GOAL_TOKENS = [
    # Сильные
    "беру", "заказываю", "оформляю", "оплачиваю", "покупаю",
    "договорились", "давайте оформим", "приступайте", "оформляйте",
    # Средние
    "согласен", "согласна", "подходит", "устраивает",
    "готов", "как оплатить", "куда платить", "давайте",
    # Слабые
    "по рукам", "ок", "хорошо беру", "то что нужно",
    "идеально", "супер",
]


# ─── Маркеры отказа ───────────────────────────────────────────────
# Фразы-маркеры «сделка не состоится», ищем как отдельные фразы.
REFUSAL_PHRASES = [
    "не беру", "не буду", "не надо", "не интересно",
    "не подходит", "не устраивает", "не готов", "не нужно",
    "не актуально", "неактуально",
    "слишком дорого",
    "отказываюсь",
    "надо подумать", "подумаю",
    "не сейчас", "позже",
]

# Слова-отказы, которые могут быть и оговоркой → отдельно
# (например, «дорого» само по себе не отказ, а «слишком дорого» — уже да)
SOFT_REFUSAL_WORDS = [
    "дорого", "дороговато", "нет",
]


# ─── Объединённые множества ───────────────────────────────────────
STRONG_SIGNALS: Set[str] = set(ACTION + FINAL + POLITE)
MEDIUM_SIGNALS: Set[str] = set(DIRECT + CONDITIONS + READINESS + CHOICE)
WEAK_SIGNALS: Set[str] = set(EMOTIONAL)
CONDITIONAL_SIGNALS: Set[str] = set(CONDITIONAL)
REFUSAL_SIGNALS: Set[str] = set(REFUSAL_PHRASES)


# ─── Вспомогательные функции ──────────────────────────────────────

def _contains_phrase(text_norm: str, phrase: str) -> bool:
    """Проверка вхождения фразы с границами слова (не как подстрока)."""
    pattern = r"(?:^|\s)" + re.escape(phrase) + r"(?:\s|$)"
    return re.search(pattern, text_norm) is not None


def _phrase_with_negation(text_norm: str, phrase: str) -> bool:
    """
    True, если фраза встречается С предшествующим отрицанием.
    Например: «не подходит», «не буду брать», «ничего не беру».
    """
    negation_words = r"(?:не|ни|нет|никогда|ничего|ни) "
    pattern = r"(?:^|\s)" + negation_words + re.escape(phrase) + r"(?:\s|$)"
    return re.search(pattern, text_norm) is not None


def _find_all(text_norm: str, phrases: List[str], allow_negation: bool = False) -> List[str]:
    """
    Ищет все фразы из списка.
    allow_negation=False → отбрасываем фразы с отрицанием перед ними.
    """
    found = []
    for phrase in phrases:
        if _contains_phrase(text_norm, phrase):
            if not allow_negation and _phrase_with_negation(text_norm, phrase):
                # Фраза есть, но с отрицанием — не считаем согласием
                continue
            found.append(phrase)
    return found


# ─── Основные функции ─────────────────────────────────────────────

def find_goal_tokens(text: str) -> List[str]:
    """Возвращает список найденных токенов цели (без отрицаний)."""
    norm = normalize(text)
    if not norm:
        return []
    return _find_all(norm, GOAL_TOKENS, allow_negation=False)


def find_refusal_tokens(text: str) -> List[str]:
    """Возвращает список найденных маркеров отказа."""
    norm = normalize(text)
    if not norm:
        return []
    found = _find_all(norm, REFUSAL_PHRASES, allow_negation=True)
    # Дополнительно — «слишком дорого» уже в списке,
    # одиночное «дорого» тоже отказ, если нет оговорки-согласия рядом
    for word in SOFT_REFUSAL_WORDS:
        if _contains_phrase(norm, word):
            found.append(word)
    return found


def classify_signal(text: str) -> Dict[str, List[str]]:
    """Классифицирует сигнал в тексте."""
    norm = normalize(text)
    result = {
        "strong": [],
        "medium": [],
        "weak": [],
        "conditional": [],
        "refusal": [],
    }
    if not norm:
        return result

    result["strong"]      = _find_all(norm, list(STRONG_SIGNALS))
    result["medium"]      = _find_all(norm, list(MEDIUM_SIGNALS))
    result["weak"]        = _find_all(norm, list(WEAK_SIGNALS))
    result["conditional"] = _find_all(norm, list(CONDITIONAL_SIGNALS))
    result["refusal"]     = _find_all(norm, REFUSAL_PHRASES, allow_negation=True)

    # Одиночное «дорого» — тоже сигнал отказа
    for word in SOFT_REFUSAL_WORDS:
        if _contains_phrase(norm, word):
            result["refusal"].append(word)

    return result


def score_goal(text: str) -> int:
    """
    Оценка силы сигнала согласия: 0–100.
    
    Приоритет:
      1. Условное согласие («да, но...») — 30–60
      2. Явный отказ                    — 0
      3. Сильный сигнал                 — 80–100
      4. Средний                        — 50–79
      5. Слабый                         — 20–49
    """
    signals = classify_signal(text)

    # 1. Условное согласие — ПЕРЕД отказом
    if signals["conditional"]:
        return min(60, 40 + 10 * len(signals["conditional"]))

    # 2. Отказ — если условного согласия нет
    if signals["refusal"]:
        return 0

    # 3. Сильный
    if signals["strong"]:
        return min(100, 80 + 5 * len(signals["strong"]))

    # 4. Средний
    if signals["medium"]:
        return min(79, 50 + 5 * len(signals["medium"]))

    # 5. Слабый
    if signals["weak"]:
        return min(49, 20 + 5 * len(signals["weak"]))

    return 0


def is_goal_achieved(text: str, threshold: int = 50) -> bool:
    """True, если сигнал согласия достаточно сильный."""
    return score_goal(text) >= threshold


def is_refusal(text: str) -> bool:
    """True, если в тексте явный отказ БЕЗ условного согласия."""
    signals = classify_signal(text)
    if signals["conditional"]:
        return False
    return len(signals["refusal"]) > 0
