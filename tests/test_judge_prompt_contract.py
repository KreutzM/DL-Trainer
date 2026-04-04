from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from codex_cli_support_mvp_common import JUDGE_PROMPT_VERSION


def test_judge_prompt_contract_covers_step_by_step_hardening() -> None:
    prompt_text = (ROOT / "prompts" / "teacher" / "jaws_de_support_judge.md").read_text(encoding="utf-8")

    assert JUDGE_PROMPT_VERSION == "jaws_de_support_judge_v3"
    assert "fehlender letzter entscheidender Schritt" in prompt_text
    assert "Vermischung verschiedener Prozeduren" in prompt_text
    assert "weniger schwerwiegend als inhaltliche Unvollstaendigkeit" in prompt_text
    assert "fachliche Vollstaendigkeit, korrekte Reihenfolge und saubere Trennung der Prozedur Vorrang" in prompt_text
    assert "gelten nur fuer `task_type=step_by_step`" in prompt_text
    assert "nicht nach `step_by_step`-Massstaeben bewerten" in prompt_text
    assert "Bei `faq_direct_answer` sind vor allem inhaltliche Korrektheit" in prompt_text
