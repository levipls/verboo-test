import re
import unicodedata
from typing import Optional

def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def normalize(s: str) -> str:
    s = (s or "").strip().lower()
    s = strip_accents(s)
    s = re.sub(r"\s+", " ", s)
    return s

def tokenize(t: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", t)

def _phrase_hits(t: str, patterns: list[str]) -> int:
    return sum(1 for rx in patterns if re.search(rx, t))


POS_WORDS = {
    "otimo","excelente","bom","maravilhoso","adorei","gostei","perfeito",
    "recomendo","rapido","eficiente","top","amei","satisfeito","parabens"
}
NEG_WORDS = {
    "ruim","pessimo","lento","demorado","horrivel","odiei","reclamar","reclamacao",
    "insuportavel","erro","bug","problema","atraso","defeito","triste","decepcionado"
}

NEG_PHRASES = [
    r"\bnao\s+gostei\b",
    r"\bnao\s+recomendo\b",
    r"\bpoderia\s+melhorar\b",
    r"\bnao\s+foi\s+bom\b",
    r"\bnunca\s+(chegou|funcionou|voltou)\b",
    r"\batras(o|ou)\b",
    r"\bdemor(a|ado|ou)\b",
    r"\bpior(?!\s*que\s*nada)\b",
]

POS_PHRASES = [
    r"\bmuito\s+bom\b",
    r"\btudo\s+certo\b",
    r"\bfuncionou\s+bem\b",
    r"\bamei\b",
]

NEGATORS = {"nao","nunca","jamais","sem","nada","nenhum","nem"}
CONTRAST = {"mas","porem","porém","contudo","entretanto","no","entanto"}


def classify_feedback(message: str) -> str:
    """
    Regras:
      1) Frases negativas fortes => complaint imediato.
      2) Contagem de termos com negação escopada (~3 palavras seguintes).
      3) Conectivos de contraste resetam contagens (peso maior ao trecho final).
      4) Sinais de rating: 1–2/5 pesa negativo; 4–5/5 pesa positivo.
      5) Desempate: se existir qualquer sinal negativo, decide complaint; senão compliment.
    """
    t = normalize(message)

    if _phrase_hits(t, NEG_PHRASES) > 0:
        return "complaint"

    pos = neg = 0
    scope = 0  
    tokens = tokenize(t)

    for tok in tokens:
        if tok in CONTRAST:
            pos = 0
            neg = 0
            scope = 0
            continue

        if tok in NEGATORS:
            scope = 3
            continue

        polarity = 0
        if tok in POS_WORDS:
            polarity = 1
        elif tok in NEG_WORDS:
            polarity = -1

        if polarity != 0:
            if scope > 0:
                polarity *= -1
                scope -= 1
            if polarity > 0:
                pos += 1
            else:
                neg += 1
        else:
            if scope > 0:
                scope -= 1

    if re.search(r"\b([12])\s*/\s*5\b", t) or re.search(r"\bnota\s*[12]\b", t):
        neg += 2
    if re.search(r"\b([45])\s*/\s*5\b", t) or re.search(r"\bnota\s*[45]\b", t):
        pos += 2

    if neg > pos:
        return "complaint"
    if pos > neg:
        return "compliment"

    if any(w in t for w in ["ruim","pessimo","horrivel","problema","erro","demora","atraso","defeito","reclamacao","nao","nunca"]):
        return "complaint"

    return "compliment"


def extract_franchise(text: str) -> Optional[str]:
    """
    Tenta extrair o nome da franquia de frases como:
    - "sou do hot burguer e queria dar um feedback"
    - "quero falar da franquia hot burguer aldeota"
    - "na loja hot burguer unidade centro"
    Heurística: pega o trecho após (franquia|loja|unidade|do|da|de|no|na)
    e corta quando aparecem conectores comuns.
    """
    if not text:
        return None
    t = normalize(text)

    m = re.search(r'\b(?:franquia|loja|unidade)\s+([a-z0-9][\w\s\-\&\.\']+)', t)
    if m:
        candidate = m.group(1)
    else:
        m = re.search(r'\b(?:do|da|de|no|na)\s+([a-z0-9][\w\s\-\&\.\']+)', t)
        if not m:
            return None
        candidate = m.group(1)

    STOP = {"e","que","pra","para","por","sobre","quero","queria","venho","gostaria",
            "dar","fazer","enviar","um","uma","o","a","os","as","feedback","reclamar",
            "reclamacao","elogio","sobre","da","de","do"}
    tokens, out = candidate.split(), []
    for tok in tokens:
        if tok in STOP:
            break
        out.append(tok)

    franchise = " ".join(out).strip(" .,-_")
    return franchise or None
