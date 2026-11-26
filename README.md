# odoo-payroll

Svensk lön för Odoo — fem moduler på `vertelab/odoo-payroll`.

All versionsberoende kod är **p-filer** (`*.p.py`, `*.p.xml`, `*.p.csv`).
P-filen är originalet på alla grenar; utdata (`*.py`, `*.xml`, `*.csv`)
genereras per gren och committas men redigeras aldrig för hand.

```
x.p.py  ──preprocess -D VERSION=18.0──▶  x.py   (committas på 18.0)
        ──preprocess -D VERSION=19.0──▶  x.py   (committas på 19.0)
        ──preprocess -D VERSION=20.0──▶  x.py   (committas på 20.0)
```

## Moduler

| Modul | Vad den gör |
|---|---|
| `hr_expense_journal_selection` | Låter ett utlägg (`hr.expense`) välja journal |
| `hr_payroll_benefits` | Förmåner på avtalet (`benefit_value()` i löneregler) |
| `hr_payroll_employeefund` | Personalfond på avtalet (analytiskt konto) |
| `hr_weekly_working_hours` | Veckoarbetstid och sysselsättningsgrad på avtalet |
| `payroll_driving_record` | Körjournal som blir utlägg |

## Porteringsstatus

Mätt 2026-11-26. Statusen bygger på **bevis**: modulen är installerad i
databasen för utgåvan, och p-filerna finns på grenen.

| Modul | 18.0 | 19.0 | 20.0 |
|---|---|---|---|
| `hr_expense_journal_selection` | ✅ porterad | ⛔ blockerad | ⛔ blockerad |
| `hr_payroll_benefits` | ✅ porterad | ⛔ blockerad | ⛔ blockerad |
| `hr_payroll_employeefund` | ✅ porterad | ⛔ blockerad | ⛔ blockerad |
| `hr_weekly_working_hours` | ✅ porterad | ⛔ blockerad | ⛔ blockerad |
| `payroll_driving_record` | ✅ porterad | ⛔ blockerad | ⛔ blockerad |

**18.0** är verifierad i `pfile_18.0`: alla fem modulerna är `installed`.

**19.0 och 20.0** är p-filsberedda (villkoren finns, utdata genereras) men
kan inte installeras eftersom beroendekedjan inte är porterad. Se
blockerarlistan nedan.

### Blockerare

Klass 1 = grenen finns men är en tomstubbe · klass 2 = grenen/modulen saknas ·
klass 3 = kärnmodulen är borttagen eller ersatt.

| Beroende | Repo | 18.0 | 19.0 | 20.0 | Klass |
|---|---|---|---|---|---|
| `payroll` | OCA/payroll | 144 filer | 141 filer | **0 filer** (bara `.github`) | 1 |
| `l10n_se_hr_payroll` | vertelab/odoo-l10n_se_payroll | ✅ | **tom gren** | **bär `18.0.1.0.1`** | 1 |
| `hr_timesheet_sheet` | OCA/timesheet | ✅ (i 18.0) | 0 filer | 0 filer | 2 |
| `hr_contract` | kärnan | ✅ | **borttagen** → `hr.version` | **borttagen** → `hr.version` | 3 |
| `account_journal_select_payable_receivable_account` | vertelab | ✅ | okänd | finns men `uninstalled` | 2 |

`payroll` (klass 1) blockerar **alla fem** modulerna i 20.0 — det är den
dyraste enskilda blockeraren i repot. `l10n_se_hr_payroll` (klass 1) blockerar
`hr_payroll_benefits` i både 19.0 och 20.0.

## Vad som skiljer mellan utgåvorna

| Brott | Villkor i p-filen |
|---|---|
| `hr_contract` borttagen → `hr.version` | `# #if VERSION >= "19.0"` |
| `hr.expense.journal_id` ägs av kärnan | `# #if VERSION < "19.0"` |
| `_create_sheet_from_expenses` → `action_submit` | `# #if VERSION < "19.0"` |
| `hr_timesheet.sheet` saknas | `# #if VERSION < "19.0"` |
| `ir.rule` borttagen → `ir.access` | `# #if VERSION >= "20.0"` |
| `ir.model.access.csv` → `ir.access.csv` | `# #if VERSION >= "20.0"` |
| `hr.version` har ingen egen form-view | `# #if VERSION < "19.0"` |

## Grind

`.github/pfiles-check.py` fäller stale utdata, p-fil utan utdata och
oförklarade källfiler. `.githooks/pre-commit` kör grinden för grenens utgåva
på **hela repot** vid varje commit (inte bara staged p-filer — en
handredigerad utdatafil committas utan att dess p-fil rörs).

```bash
# Aktivera hooken i en ny klon
git config core.hooksPath .githooks

# Kör grinden manuellt för en utgåva
python3 .github/pfiles-check.py --version 18.0 -q .
```

`.pfiles-allow` listar filer som inte är p-filer: genererad `index.html`,
20.0-filen `ir.access.csv` (laddas aldrig i 18/19), och Flutter-appen.

## Expansion

```bash
# En fil
rm -f modul/models/x.py
preprocess -f -D VERSION=18.0 -o modul/models/x.py modul/models/x.p.py

# Alla p-filer i repot, för en utgåva
find . -path ./.git -prune -o \( -name '*.p.py' -o -name '*.p.xml' -o -name '*.p.csv' \) -print |
while read p; do
  case "$p" in
    *.p.py)  o="${p%.p.py}.py"   ;;
    *.p.xml) o="${p%.p.xml}.xml" ;;
    *.p.csv) o="${p%.p.csv}.csv" ;;
  esac
  rm -f "$o"; preprocess -f -D VERSION=18.0 -o "$o" "$p"
done
```

⚠ `preprocess --version` är verktygets egen flagga — den expanderar ingenting
och ger exit 0. Använd alltid `-D VERSION=<utgåva>`.

⚠ Utdata är **gemensam** mellan utgåvor i en arbetskatalog. Expandera för rätt
utgåva precis före testet, aldrig i en loop som slutar med en annan utgåva.
