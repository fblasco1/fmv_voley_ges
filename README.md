# fmv_voley_ges

Extractor de **fixtures de vóley FMV** ([metrovoley.com.ar](https://metrovoley.com.ar)) para **Inst. Cult. Dep. Pedro Echagüe** (club FMV `420`).

Publica JSON en el contrato consumido por **SICLUB** (`club_management` → módulo Spaces), análogo a [`formativas_ges`](https://github.com/fblasco1/formativas_ges) para básquet FeBAMBA.

## Fuente

| Campo | Valor |
|-------|-------|
| URL | https://metrovoley.com.ar/clubs/420/matches |
| `club_id_fmv` | `420` |
| Tecnología | Laravel + Inertia.js (JSON embebido en `data-page`) |

No hay API pública documentada: el scraper parsea el HTML SSR de cada página de partidos.

## Salida

| Archivo | Uso |
|---------|-----|
| `outputs/echague/fixture_fmv_voley.json` | SICLUB (`fmv_voley.py`) vía raw GitHub |
| `outputs/echague/fixture_fmv_voley.csv` | Revisión manual / Coordinación |

## Reglas de cancha (locales en Portela)

| Equipo FMV | Espacio SICLUB |
|------------|----------------|
| `Superiores` + `ECHAGÜE` (sin B) | **Cancha 1** |
| `ECHAGÜE B` y resto | **Cancha 2** |

Partidos **visitante** se incluyen en el JSON con `localia: Visitante` (SICLUB no ocupa espacio).

## Uso local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install pytest  # opcional

python analysis/sync_fixture_echague.py
pytest
```

Opciones:

```bash
python analysis/sync_fixture_echague.py --solo-local   # solo partidos en Portela
python analysis/sync_fixture_echague.py --no-csv
```

## CI

Workflow `.github/workflows/sync_echague.yml`: corre a las **08:00 y 20:00 ART** y commitea cambios en `outputs/`.

## Consumo en SICLUB (pendiente adaptador)

URL canónica prevista:

```text
https://raw.githubusercontent.com/fblasco1/fmv_voley_ges/main/outputs/echague/fixture_fmv_voley.json
```

Ver `club_management/specs/spaces_fixtures_partidos.md` § sync FMV.

## Licencia

Uso interno ICDPE / ERSport. Respetar términos de metrovoley.com.ar; scraping moderado (delay entre páginas).
