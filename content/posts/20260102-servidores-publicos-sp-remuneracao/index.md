---
title: "Construindo um Pipeline ETL de Dados Públicos: Análise da Remuneração do Estado de SP com Python"
author: Komesu, D. K.
slug: servidores-publicos-sp-remuneracao
date: 2026-01-02T12:00:00-03:00
lastmod: 2026-10-27T21:00:00-03:00
categories: ["Data Science", "Python", "Economia"]
tags: ["ETL", "Dados Abertos", "Pandas", "São Paulo", "Governo"]
description: "Tutorial completo de como construir um pipeline ETL em Python para baixar, processar e analisar dados de remuneração dos servidores públicos do Estado de São Paulo."
---

A transparência fiscal é um dos pilares da democracia moderna e da eficiência econômica. No Brasil, a **Lei de Acesso à Informação (LAI - Lei nº 12.527/2011)** transformou a relação entre o Estado e a sociedade, obrigando entes públicos a disponibilizarem dados detalhados sobre suas despesas, incluindo a folha de pagamento.

Para economistas, cientistas políticos e engenheiros de dados, o [Portal da Transparência do Estado de São Paulo](https://www.transparencia.sp.gov.br/Home/Remuneracao) oferece um conjunto de dados valioso (dataset) para investigar a alocação de recursos humanos, a evolução da massa salarial e a desigualdade no setor público.

No entanto, a **acessibilidade** não garante a **usabilidade**. Os dados frequentemente são disponibilizados em formatos legados ou fragmentados, exigindo um tratamento robusto antes de qualquer análise econométrica. Neste artigo, apresentaremos uma arquitetura de **Engenharia de Dados** para implementar um pipeline **ETL (Extract, Transform, Load)** completo utilizando Python.

## O Desafio da Engenharia de Dados: Dados Fragmentados e Legados

O principal obstáculo ao analisar a remuneração dos servidores de São Paulo é a fragmentação e o formato de armazenamento:

1. **Fragmentação Temporal:** Os dados são publicados mês a mês, um arquivo por mês, desde junho de 2012.
2. **Dois canais de publicação:** A série histórica, de junho de 2012 a março de 2026, está em arquivos `.rar` que não aparecem na página atual do portal. Os meses seguintes saem num canal novo, em `.zip`, listado na aba "Histórico" da página.
3. **Esquema instável:** Os nomes e a quantidade de colunas mudaram sete vezes desde 2012, e a codificação passou de `latin-1` para UTF-8 em 2026.

Realizar o download e a unificação manual de quase 15 anos de histórico (mais de 160 arquivos, cerca de 3 GB comprimidos) é inviável e propenso a erro humano. A automação via Python não é apenas uma conveniência, é uma necessidade metodológica para garantir a reprodutibilidade da pesquisa.

## Stack Tecnológico

Utilizaremos uma *stack* focada em eficiência de I/O e processamento vetorial:

* **Python 3.10+**: Linguagem core.
* **Pandas**: Para manipulação tabular em memória.
* **Httpx**: Cliente HTTP moderno, com *streaming* de respostas e controle fino de *timeouts*.
* **libarchive** (via `libarchive-c`): Lê `.rar` e `.zip` com a mesma interface. Prefira-a ao 7-Zip: em várias distribuições Linux (o Fedora, por exemplo) o `7z` do sistema vem sem o codec RAR e não abre esses arquivos.
* **PyArrow/Parquet**: Formato de armazenamento colunar que reduz drasticamente o espaço em disco e acelera leituras futuras.

Instalação:

```bash
pip install httpx pandas pyarrow tqdm libarchive-c
```

O pacote `libarchive-c` precisa da biblioteca `libarchive` do sistema, que já vem instalada na maioria das distribuições Linux.

---

## Implementação do Pipeline

### 1. Configuração e Definição de Escopo

O primeiro passo de um pipeline robusto é a definição de constantes. Isso evita *hardcoding* (valores fixos espalhados pelo código) e facilita a manutenção caso a URL do portal mude no futuro — o que, como veremos, já aconteceu.

```python
import datetime as dt
import html
import io
import re
from pathlib import Path

import httpx
import libarchive
import pandas as pd
from tqdm import tqdm

PORTAL = "https://www.transparencia.sp.gov.br"
# Série histórica em RAR, de junho de 2012 a março de 2026.
RAR_URL = PORTAL + "/PortalTransparencia-Report/historico/remuneracao_{month_name}_{year}.rar"
# Canal novo (ZIP). O id não segue o mês: o par mês→id vem da aba "Histórico" desta página.
HISTORICO_URL = PORTAL + "/Home/Remuneracao"
ZIP_URL = PORTAL + "/Remuneracao/downloadhistorico?id={id}&f=zip"
MONTHS = {
    "Janeiro": 1,
    "Fevereiro": 2,
    "Março": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12,
}
START = (2012, 6)

RAW_DIR = Path("data/raw")
PARQUET_DIR = Path("data/parquet")
HEADERS = {"User-Agent": "Mozilla/5.0"}
```

### 2. A Camada de Extração (Extract)

A extração de dados governamentais frequentemente exige lidar com inconsistências nas URLs. Um exemplo clássico encontrado neste portal é a grafia do mês de março: o arquivo se chama `Março` até 2016 e `Marco`, sem cedilha, de 2017 em diante.

```python
def periodos(hoje: dt.date | None = None) -> list[tuple[int, int]]:
    """Meses de junho de 2012 até o mês corrente."""
    hoje = hoje or dt.date.today()
    year, month = START
    out = []
    while (year, month) <= (hoje.year, hoje.month):
        out.append((year, month))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return out


def get_rar_url(year: int, month: int) -> str:
    month_name = next(name for name, num in MONTHS.items() if num == month)
    # A partir de 2017 o arquivo de março perde a cedilha.
    if year >= 2017 and month == 3:
        month_name = "Marco"
    return RAR_URL.format(year=year, month_name=month_name)
```

O canal novo não segue o mês na URL: cada arquivo tem um `id` numérico, e a sequência tem buracos (o id 65 não é usado). Por isso o pipeline lê o par mês → id da própria página, em vez de calculá-lo:

```python
def indice_zip(client: httpx.Client) -> dict[tuple[int, int], int]:
    """Lê a aba "Histórico" da página e devolve {(ano, mês): id}."""
    page = client.get(HISTORICO_URL)
    page.raise_for_status()
    nomes = {name.lower(): num for name, num in MONTHS.items()}
    rows = re.findall(
        r"<strong>\s*(\d{4})\s*-\s*([^<]+?)\s*</strong>\s*</td>\s*<td[^>]*>\s*"
        r'<a href="/Remuneracao/downloadhistorico\?id=(\d+)',
        page.text,
    )
    return {
        (int(year), nomes[html.unescape(month).lower()]): int(zip_id)
        for year, month, zip_id in rows
    }
```

A função `baixar` gerencia a transferência de bytes, utilizando `stream` para evitar carregar arquivos grandes inteiramente na memória RAM. O arquivo é gravado primeiro com a extensão `.part` e só é renomeado quando o download termina: se o script for interrompido no meio, nenhum arquivo truncado fica para trás.

```python
def baixar(client: httpx.Client, url: str, dest: Path) -> bool:
    """Baixa para um .part e renomeia no fim: interrupção nunca deixa arquivo truncado."""
    part = dest.with_name(dest.name + ".part")
    with client.stream("GET", url) as r:
        if r.status_code == 404:
            return False
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0)) or None
        with (
            open(part, "wb") as f,
            tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar,
        ):
            for chunk in r.iter_bytes():
                f.write(chunk)
                bar.update(len(chunk))
    part.replace(dest)
    return True
```

A orquestração do download (`download_data`) garante a **idempotência** do processo: se o script for interrompido e rodado novamente, ele pula os meses que já estão no disco e baixa só o que falta. Para cada mês, tenta primeiro a série RAR e, se ela não tiver o arquivo, o canal ZIP. Erros de rede e respostas transitórias do portal (ele às vezes responde 405 ou 503) não interrompem o laço: o mês é tentado de novo na próxima execução.

```python
def download_data(meses: list[tuple[int, int]] | None = None) -> None:
    """Baixa cada mês: primeiro a série RAR; se não houver, o canal ZIP."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_ids = None
    with httpx.Client(headers=HEADERS, timeout=httpx.Timeout(60), follow_redirects=True) as client:
        for year, month in meses or periodos():
            stem = f"{year}{month:02}"
            if any((RAW_DIR / f"{stem}{ext}").exists() for ext in (".rar", ".zip")):
                continue
            try:
                if baixar(client, get_rar_url(year, month), RAW_DIR / f"{stem}.rar"):
                    continue
                if zip_ids is None:
                    try:
                        zip_ids = indice_zip(client)
                    except httpx.HTTPError as e:
                        print(f"Não foi possível ler o índice do canal ZIP: {e}")
                        zip_ids = {}
                zip_id = zip_ids.get((year, month))
                if zip_id is None or not baixar(
                    client, ZIP_URL.format(id=zip_id), RAW_DIR / f"{stem}.zip"
                ):
                    print(f"{month:02}/{year}: não publicado.")
            except httpx.HTTPError as e:
                # 405/503 transitórios do portal e timeouts: tenta de novo na próxima execução.
                print(f"{month:02}/{year}: falha no download ({e}).")
```

### 3. Transformação e Limpeza (Transform)

Esta é a etapa mais crítica. A `libarchive` lê o único arquivo de texto de dentro do `.rar` ou do `.zip` direto para a memória, sem diretório temporário.

A padronização dos nomes das colunas é vital. Em séries temporais longas, é comum que o órgão público mude a nomenclatura das colunas. Neste caso, foram sete variações de cabeçalho:

| Período | Colunas de valor | Particularidade |
|---|---|---|
| jun–dez/2012 | `TOTDOMES`, `TOTBRUTO`, `TOTLIQ` | 6 colunas |
| 2013–2016 | `TOTMES_FINAL`, `TOTBRU_FINAL`, `TOTLIQ_FINAL` | 6 colunas |
| 2017–2019 | `REMUNERAÇÃO DO MÊS`, … , `TOTAL LIQUÍDO (R$)` | 10 colunas, com o detalhamento de férias, eventuais, licença-prêmio, abono e redutor |
| 2020–2021 | idem | + `SITUAÇÃO` (ativos, aposentados, pensionistas) |
| 2022 – mar/2026 | idem | `SITUAÇÃO` passa a se chamar `GRUPO` |
| abr e mai/2026 (ZIP) | `REMUNERAÇÃO`, … , `RENDIMENTO LÍQUIDO` | 18 colunas, UTF-8; maio saiu **sem a linha de cabeçalho** |
| jun/2026 em diante (ZIP) | nomes de 2017 | 19 colunas, com `CPF` mascarado |

O dicionário `RENAME` leva todas para um mesmo vocabulário. Sem essa normalização, a concatenação futura dos dados misturaria colunas equivalentes com nomes diferentes. A codificação é detectada pelo BOM do UTF-8, e o separador de milhar (`1.400,00`, que aparece nos arquivos de 2026) é tratado pelo `thousands="."`. O CPF mascarado é descartado: ele só existe em alguns meses e não tem uso analítico.

```python
# Nomes canônicos para as sete variações de cabeçalho publicadas desde 2012.
RENAME = {
    "ORGAO": "ÓRGÃO",
    "ORGÃO": "ÓRGÃO",
    "TOTDOMES": "REMUNERAÇÃO DO MÊS",
    "TOTMES_FINAL": "REMUNERAÇÃO DO MÊS",
    "REMUNERAÇÃO": "REMUNERAÇÃO DO MÊS",
    "TOTBRUTO": "TOTAL BRUTO",
    "TOTBRU_FINAL": "TOTAL BRUTO",
    "TOTLIQ": "TOTAL LÍQUIDO",
    "TOTLIQ_FINAL": "TOTAL LÍQUIDO",
    "TOTAL LIQUÍDO (R$)": "TOTAL LÍQUIDO",
    "RENDIMENTO LÍQUIDO": "TOTAL LÍQUIDO",
    "FÉRIAS/13º": "FÉRIAS E 13º SALÁRIO",
    "LICENÇA PRÊMIO": "LICENÇA PRÊMIO INDENIZADA",
    "ABONO PERMANÊNCIA": "ABONO PERMANÊNCIA & OUTRAS INDENIZAÇÕES",
    "REDUTOR": "REDUTOR SALARIAL",
    "SITUAÇÃO": "GRUPO",  # 2020-2021: ATIVOS, APOSENTADOS, PENSIONISTAS
    "SITUAÇÃO DE DESLIGAMENTO": "SITUAÇÃO FUNCIONAL",
    "JORNADA DE TRABALHO": "JORNADA",
    "REFERENCIA": "REFERÊNCIA",
    "DATA DE INGRESSO": "INGRESSO",
    "DATA DE NOMEAÇÃO NO CARGO": "NOMEAÇÃO",
    "NOMEACAO": "NOMEAÇÃO",
}


# Pelo menos um mês (maio de 2026) saiu sem a linha de cabeçalho.
SEM_CABECALHO = {
    18: [
        "NOME",
        "CARGO",
        "ORGÃO",
        "REMUNERAÇÃO",
        "FÉRIAS/13º",
        "PAGAMENTOS EVENTUAIS",
        "LICENÇA PRÊMIO",
        "ABONO PERMANÊNCIA",
        "REDUTOR",
        "RENDIMENTO LÍQUIDO",
        "GRUPO",
        "SITUAÇÃO FUNCIONAL",
        "REGIME DE CONTRATAÇÃO",
        "JORNADA DE TRABALHO",
        "REFERENCIA",
        "GRAU",
        "DATA DE INGRESSO",
        "DATA DE NOMEAÇÃO NO CARGO",
    ],
}


def read_remuneracao(file: Path) -> pd.DataFrame:
    """Lê o único arquivo de texto dentro do RAR ou do ZIP e normaliza as colunas."""
    with libarchive.file_reader(str(file)) as archive:
        for entry in archive:
            if entry.isfile:
                content = b"".join(entry.get_blocks())
                break
    # Série RAR e ZIPs até 2025: latin-1. ZIPs de 2026: UTF-8 com BOM.
    encoding = "utf-8-sig" if content.startswith(b"\xef\xbb\xbf") else "latin-1"
    first_line = content.split(b"\n", 1)[0].decode(encoding).strip().split(";")
    header, names = 0, None
    if first_line[0] != "NOME":
        header = None
        try:
            names = SEM_CABECALHO[len(first_line)]
        except KeyError:
            msg = f"{file.name}: layout sem cabeçalho com {len(first_line)} colunas"
            raise ValueError(msg) from None
    df = pd.read_csv(
        io.BytesIO(content),
        sep=";",
        decimal=",",
        thousands=".",
        encoding=encoding,
        header=header,
        names=names,
    )
    # O CPF (mascarado) só aparece em alguns meses de 2026 e não serve à análise.
    return df.rename(columns=RENAME).drop(columns=["CPF"], errors="ignore")
```

### 4. Carga Otimizada (Load): Por que Parquet?

Muitos economistas mantêm seus dados em CSV ou Excel. No entanto, para *Data Science* e *Big Data*, o formato **Apache Parquet** é superior por dois motivos:

1. **Armazenamento Colunar:** Permite ler apenas as colunas necessárias para uma análise (ex: carregar apenas a coluna "REMUNERAÇÃO DO MÊS" sem ler "NOME"), economizando memória.
2. **Compressão:** Arquivos Parquet costumam ser até 90% menores que CSVs correspondentes, mantendo os tipos de dados (inteiro, float, string) preservados.

Um detalhe que passa despercebido: **nenhum arquivo traz a data de referência**. O mês só existe no nome do arquivo. Por isso a conversão grava a coluna `ANO_MES`; sem ela, ao juntar os meses, o período se perderia.

A conversão também confere a qualidade da publicação. Em todo mês há algumas linhas repetidas (homônimos com o mesmo cargo e salário, cerca de 0,01% do total), mas uma taxa acima de 1% indica arquivo defeituoso. Isso já aconteceu: o arquivo de **maio de 2026 foi publicado com os dados de abril repetidos duas vezes** (verificado em outubro de 2026), e o pipeline avisa.

```python
def convert_to_parquet() -> None:
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW_DIR.glob("*.rar")) + sorted(RAW_DIR.glob("*.zip"))
    for file in tqdm(files, desc="Convertendo"):
        dest = PARQUET_DIR / f"{file.stem}.parquet"
        if dest.exists():
            continue
        try:
            df = read_remuneracao(file)
            # Homônimos com o mesmo salário somam ~0,01% das linhas. Acima de 1% é
            # publicação defeituosa (maio de 2026 saiu como abril repetido duas vezes).
            if (dup := df.duplicated().mean()) > 0.01:
                print(f"Aviso: {file.name} tem {dup:.0%} de linhas duplicadas; confira a fonte.")
            # O mês de referência só existe no nome do arquivo: sem esta coluna,
            # a concatenação dos meses perde o período.
            df.insert(0, "ANO_MES", pd.Timestamp(f"{file.stem[:4]}-{file.stem[4:]}-01"))
            part = dest.with_name(dest.name + ".part")
            df.to_parquet(part)
            part.replace(dest)
        except Exception as e:
            print(f"Erro em {file.name}: {e}")
```

## O Código Completo

Para facilitar sua implementação, segue o script unificado. Salve-o como `etl_servidores.py`. Na primeira execução ele baixa cerca de 3 GB.

```python
import datetime as dt
import html
import io
import re
from pathlib import Path

import httpx
import libarchive
import pandas as pd
from tqdm import tqdm

PORTAL = "https://www.transparencia.sp.gov.br"
# Série histórica em RAR, de junho de 2012 a março de 2026.
RAR_URL = PORTAL + "/PortalTransparencia-Report/historico/remuneracao_{month_name}_{year}.rar"
# Canal novo (ZIP). O id não segue o mês: o par mês→id vem da aba "Histórico" desta página.
HISTORICO_URL = PORTAL + "/Home/Remuneracao"
ZIP_URL = PORTAL + "/Remuneracao/downloadhistorico?id={id}&f=zip"

MONTHS = {
    "Janeiro": 1,
    "Fevereiro": 2,
    "Março": 3,
    "Abril": 4,
    "Maio": 5,
    "Junho": 6,
    "Julho": 7,
    "Agosto": 8,
    "Setembro": 9,
    "Outubro": 10,
    "Novembro": 11,
    "Dezembro": 12,
}
START = (2012, 6)

RAW_DIR = Path("data/raw")
PARQUET_DIR = Path("data/parquet")
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Nomes canônicos para as sete variações de cabeçalho publicadas desde 2012.
RENAME = {
    "ORGAO": "ÓRGÃO",
    "ORGÃO": "ÓRGÃO",
    "TOTDOMES": "REMUNERAÇÃO DO MÊS",
    "TOTMES_FINAL": "REMUNERAÇÃO DO MÊS",
    "REMUNERAÇÃO": "REMUNERAÇÃO DO MÊS",
    "TOTBRUTO": "TOTAL BRUTO",
    "TOTBRU_FINAL": "TOTAL BRUTO",
    "TOTLIQ": "TOTAL LÍQUIDO",
    "TOTLIQ_FINAL": "TOTAL LÍQUIDO",
    "TOTAL LIQUÍDO (R$)": "TOTAL LÍQUIDO",
    "RENDIMENTO LÍQUIDO": "TOTAL LÍQUIDO",
    "FÉRIAS/13º": "FÉRIAS E 13º SALÁRIO",
    "LICENÇA PRÊMIO": "LICENÇA PRÊMIO INDENIZADA",
    "ABONO PERMANÊNCIA": "ABONO PERMANÊNCIA & OUTRAS INDENIZAÇÕES",
    "REDUTOR": "REDUTOR SALARIAL",
    "SITUAÇÃO": "GRUPO",  # 2020-2021: ATIVOS, APOSENTADOS, PENSIONISTAS
    "SITUAÇÃO DE DESLIGAMENTO": "SITUAÇÃO FUNCIONAL",
    "JORNADA DE TRABALHO": "JORNADA",
    "REFERENCIA": "REFERÊNCIA",
    "DATA DE INGRESSO": "INGRESSO",
    "DATA DE NOMEAÇÃO NO CARGO": "NOMEAÇÃO",
    "NOMEACAO": "NOMEAÇÃO",
}

# Pelo menos um mês (maio de 2026) saiu sem a linha de cabeçalho.
SEM_CABECALHO = {
    18: [
        "NOME",
        "CARGO",
        "ORGÃO",
        "REMUNERAÇÃO",
        "FÉRIAS/13º",
        "PAGAMENTOS EVENTUAIS",
        "LICENÇA PRÊMIO",
        "ABONO PERMANÊNCIA",
        "REDUTOR",
        "RENDIMENTO LÍQUIDO",
        "GRUPO",
        "SITUAÇÃO FUNCIONAL",
        "REGIME DE CONTRATAÇÃO",
        "JORNADA DE TRABALHO",
        "REFERENCIA",
        "GRAU",
        "DATA DE INGRESSO",
        "DATA DE NOMEAÇÃO NO CARGO",
    ],
}


def periodos(hoje: dt.date | None = None) -> list[tuple[int, int]]:
    """Meses de junho de 2012 até o mês corrente."""
    hoje = hoje or dt.date.today()
    year, month = START
    out = []
    while (year, month) <= (hoje.year, hoje.month):
        out.append((year, month))
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return out


def get_rar_url(year: int, month: int) -> str:
    month_name = next(name for name, num in MONTHS.items() if num == month)
    # A partir de 2017 o arquivo de março perde a cedilha.
    if year >= 2017 and month == 3:
        month_name = "Marco"
    return RAR_URL.format(year=year, month_name=month_name)


def indice_zip(client: httpx.Client) -> dict[tuple[int, int], int]:
    """Lê a aba "Histórico" da página e devolve {(ano, mês): id}."""
    page = client.get(HISTORICO_URL)
    page.raise_for_status()
    nomes = {name.lower(): num for name, num in MONTHS.items()}
    rows = re.findall(
        r"<strong>\s*(\d{4})\s*-\s*([^<]+?)\s*</strong>\s*</td>\s*<td[^>]*>\s*"
        r'<a href="/Remuneracao/downloadhistorico\?id=(\d+)',
        page.text,
    )
    return {
        (int(year), nomes[html.unescape(month).lower()]): int(zip_id)
        for year, month, zip_id in rows
    }


def baixar(client: httpx.Client, url: str, dest: Path) -> bool:
    """Baixa para um .part e renomeia no fim: interrupção nunca deixa arquivo truncado."""
    part = dest.with_name(dest.name + ".part")
    with client.stream("GET", url) as r:
        if r.status_code == 404:
            return False
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0)) or None
        with (
            open(part, "wb") as f,
            tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar,
        ):
            for chunk in r.iter_bytes():
                f.write(chunk)
                bar.update(len(chunk))
    part.replace(dest)
    return True


def download_data(meses: list[tuple[int, int]] | None = None) -> None:
    """Baixa cada mês: primeiro a série RAR; se não houver, o canal ZIP."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_ids = None
    with httpx.Client(headers=HEADERS, timeout=httpx.Timeout(60), follow_redirects=True) as client:
        for year, month in meses or periodos():
            stem = f"{year}{month:02}"
            if any((RAW_DIR / f"{stem}{ext}").exists() for ext in (".rar", ".zip")):
                continue
            try:
                if baixar(client, get_rar_url(year, month), RAW_DIR / f"{stem}.rar"):
                    continue
                if zip_ids is None:
                    try:
                        zip_ids = indice_zip(client)
                    except httpx.HTTPError as e:
                        print(f"Não foi possível ler o índice do canal ZIP: {e}")
                        zip_ids = {}
                zip_id = zip_ids.get((year, month))
                if zip_id is None or not baixar(
                    client, ZIP_URL.format(id=zip_id), RAW_DIR / f"{stem}.zip"
                ):
                    print(f"{month:02}/{year}: não publicado.")
            except httpx.HTTPError as e:
                # 405/503 transitórios do portal e timeouts: tenta de novo na próxima execução.
                print(f"{month:02}/{year}: falha no download ({e}).")


def read_remuneracao(file: Path) -> pd.DataFrame:
    """Lê o único arquivo de texto dentro do RAR ou do ZIP e normaliza as colunas."""
    with libarchive.file_reader(str(file)) as archive:
        for entry in archive:
            if entry.isfile:
                content = b"".join(entry.get_blocks())
                break
    # Série RAR e ZIPs até 2025: latin-1. ZIPs de 2026: UTF-8 com BOM.
    encoding = "utf-8-sig" if content.startswith(b"\xef\xbb\xbf") else "latin-1"
    first_line = content.split(b"\n", 1)[0].decode(encoding).strip().split(";")
    header, names = 0, None
    if first_line[0] != "NOME":
        header = None
        try:
            names = SEM_CABECALHO[len(first_line)]
        except KeyError:
            msg = f"{file.name}: layout sem cabeçalho com {len(first_line)} colunas"
            raise ValueError(msg) from None
    df = pd.read_csv(
        io.BytesIO(content),
        sep=";",
        decimal=",",
        thousands=".",
        encoding=encoding,
        header=header,
        names=names,
    )
    # O CPF (mascarado) só aparece em alguns meses de 2026 e não serve à análise.
    return df.rename(columns=RENAME).drop(columns=["CPF"], errors="ignore")


def convert_to_parquet() -> None:
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW_DIR.glob("*.rar")) + sorted(RAW_DIR.glob("*.zip"))
    for file in tqdm(files, desc="Convertendo"):
        dest = PARQUET_DIR / f"{file.stem}.parquet"
        if dest.exists():
            continue
        try:
            df = read_remuneracao(file)
            # Homônimos com o mesmo salário somam ~0,01% das linhas. Acima de 1% é
            # publicação defeituosa (maio de 2026 saiu como abril repetido duas vezes).
            if (dup := df.duplicated().mean()) > 0.01:
                print(f"Aviso: {file.name} tem {dup:.0%} de linhas duplicadas; confira a fonte.")
            # O mês de referência só existe no nome do arquivo: sem esta coluna,
            # a concatenação dos meses perde o período.
            df.insert(0, "ANO_MES", pd.Timestamp(f"{file.stem[:4]}-{file.stem[4:]}-01"))
            part = dest.with_name(dest.name + ".part")
            df.to_parquet(part)
            part.replace(dest)
        except Exception as e:
            print(f"Erro em {file.name}: {e}")


if __name__ == "__main__":
    download_data()
    convert_to_parquet()
```

## Consultando o Resultado

Os arquivos Parquet mensais têm colunas diferentes conforme o período (o detalhamento de férias, por exemplo, só existe a partir de 2017). O DuckDB lê todos de uma vez e preenche as colunas ausentes com nulos:

```python
import duckdb

duckdb.sql("""
    SELECT ANO_MES,
           count(*) AS registros,
           median("REMUNERAÇÃO DO MÊS") AS mediana,
           sum("REMUNERAÇÃO DO MÊS") / 1e9 AS massa_bilhoes
    FROM read_parquet('data/parquet/*.parquet', union_by_name = true)
    GROUP BY ANO_MES
    ORDER BY ANO_MES
""").show()
```

## Próximos Passos: Análise Econômica

Com os dados estruturados em Parquet, o caminho está livre para análises complexas. Algumas sugestões de investigação:

1. **Correção Inflacionária:** Utilizar o IPCA (via API do IBGE/Sidra) para deflacionar os salários e analisar o ganho real dos servidores ao longo da série.
2. **Clusterização:** Identificar padrões de remuneração entre diferentes órgãos (Secretaria da Fazenda vs. Educação, por exemplo). Atenção: os nomes dos órgãos também mudam ao longo do tempo (a Polícia Militar aparece como `POLICIA MILITAR ESTADO SAO PAULO` em 2012, `PM` em 2017 e `POLICIA MILITAR SAO PAULO` em 2024), então é preciso uma tabela de correspondência antes de comparar órgãos entre anos.
3. **Detecção de Anomalias:** Utilizar técnicas estatísticas (como *Z-Score* ou *Isolation Forests*) para encontrar pagamentos atípicos ("supersalários") que destoam da distribuição normal.

Este pipeline serve como base para transformar dados brutos em *insights* acionáveis de política pública.

## Referências e Bibliografia

* BRASIL. **Lei nº 12.527, de 18 de novembro de 2011**. Regula o acesso a informações previsto no inciso XXXIII do art. 5º, no inciso II do § 3º do art. 37 e no § 2º do art. 216 da Constituição Federal. Disponível em: [Planalto.gov.br](http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12527.htm).
* MCKINNEY, Wes. **Python for Data Analysis: Data Wrangling with Pandas, NumPy, and Jupyter**. 3rd Edition. O'Reilly Media, 2022.
* APACHE SOFTWARE FOUNDATION. **Apache Parquet Documentation**. Disponível em: [parquet.apache.org](https://parquet.apache.org/).
* SÃO PAULO (Estado). **Portal da Transparência: Remuneração**. Disponível em: [transparencia.sp.gov.br](https://www.transparencia.sp.gov.br/Home/Remuneracao).
