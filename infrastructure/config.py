import re

JOBS_PORTAL_URL: str = "https://www.empleospublicos.cl/apiConvocatorias.ashx?page=1&pageSize=1000&status=Abierta"
PORTAL_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

KINE_PATTERN: re.Pattern = re.compile(
    r"\bkine(?:si[oó]log[oa]s?|siolog[oa]s?|siolog[ií]as?)?\b", 
    re.IGNORECASE
)
MATRON_PATTERN: re.Pattern = re.compile(
    r"\bmatr[oó]n(?:[oa]s?|es|\([oa]\)s?|er[ií]a)?\b", 
    re.IGNORECASE
)

KINE_RECIPIENTS: list[str] = ["sepulveda.cristobal.ignacio@gmail.com"]
MATRON_RECIPIENTS: list[str] = ["sepulveda.cristobal.ignacio@gmail.com"]

SANTIAGO_PROVINCE_COMMUNES: set[str] = {
    "santiago", 
    "cerrillos", 
    "cerro navia", 
    "conchali", 
    "conchalí", 
    "el bosque", 
    "estacion central", 
    "estación central", 
    "huechuraba", 
    "independencia", 
    "la cisterna", 
    "la florida", 
    "la granja", 
    "la pintana", 
    "la reina", 
    "las condes", 
    "lo barnechea", 
    "lo espejo", 
    "lo prado", 
    "macul", 
    "maipu", 
    "maipú", 
    "nunoa", 
    "ñuñoa", 
    "pedro aguirre cerda", 
    "penalolen", 
    "peñalolén", 
    "peñalolen", 
    "providencia", 
    "pudahuel", 
    "quilicura", 
    "quinta normal", 
    "recoleta", 
    "renca", 
    "san joaquin", 
    "san joaquín", 
    "san miguel", 
    "san ramon", 
    "san ramón", 
    "vitacura"
}
